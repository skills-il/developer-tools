#!/usr/bin/env python3
"""JFrog Xray REST API Client.

A standalone client for interacting with JFrog Xray, supports vulnerability
scanning, security policy management, watch creation, violation search, and
report generation.

Requirements:
    pip install requests

Usage:
    export JFROG_XRAY_URL="https://acme.jfrog.io/xray"
    export JFROG_ACCESS_TOKEN="..."          # never pass a token on argv

    python3 xray_client.py summary --path "docker-local/nginx/latest/manifest.json"
    python3 xray_client.py trigger-scan --component-id "docker://myapp:1.0.0"
    python3 xray_client.py violations --watch prod-security-watch

Environment variables:
    JFROG_XRAY_URL: Xray base URL
    JFROG_ACCESS_TOKEN: Access token for authentication

The token is read from the environment only. It is deliberately NOT accepted as a
command-line flag: argv is world-readable through `ps` and /proc on a shared build
agent, so a flag would leak a platform-scoped JFrog token to every user on the host.

`summary` READS an existing scan result. It does not scan. An artifact that Xray has
never indexed and scanned returns an empty result, which prints as "No vulnerabilities
found" from any tool. Confirm the repository is under Xray's Indexed Resources and the
artifact's scan status is complete before you treat an empty summary as clean.
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests",
          file=sys.stderr)
    sys.exit(1)


class XrayClient:
    """Client for JFrog Xray REST API."""

    def __init__(self, base_url: str, access_token: str, timeout: int = 60):
        """Initialize Xray client.

        Args:
            base_url: Xray base URL (e.g., https://acme.jfrog.io/xray)
            access_token: JFrog access token
            timeout: per-request timeout in seconds. Never leave this unset:
                a hung connection blocks a CI job indefinitely.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })
        # JFrog SaaS rate-limits per subscription tier and answers 429 with
        # Retry-After, so calls made in a CI loop need to back off rather than
        # fail on the first throttle. Retries are split across two sessions
        # because retrying is only safe for some of them.
        #
        # self.session retries idempotent methods only. This client
        # issues no PUT and no upload; POST is excluded because
        # creating a policy or watch, or triggering a scan, must not repeat if
        # the server processed the first request and only the response failed.
        #
        # self._read_session additionally retries POST, but on 429 ALONE and
        # never on 5xx: a 429 means the request was rejected without being
        # processed, so repeating it is safe, whereas a 5xx on a POST is
        # exactly the case where the server may have acted and only the
        # response failed. get_artifact_summary, get_scan_status and get_violations are routed
        # through it: all three are reads that happen to use POST.
        self._read_session = requests.Session()
        # Snapshot, not a shared object: a future caller that refreshes the
        # token by mutating self.session.headers must update both sessions.
        self._read_session.headers.update(self.session.headers)
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            safe = Retry(total=4, backoff_factor=1.5,
                         status_forcelist=(429, 500, 502, 503, 504),
                         allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
                         respect_retry_after_header=True)
            read_only = Retry(total=4, backoff_factor=1.5,
                              status_forcelist=(429,),
                              allowed_methods=frozenset(["GET", "HEAD", "OPTIONS", "POST"]),
                              respect_retry_after_header=True)
            for scheme in ("https://", "http://"):
                self.session.mount(scheme, HTTPAdapter(max_retries=safe))
                self._read_session.mount(scheme, HTTPAdapter(max_retries=read_only))
        except Exception:  # urllib3 too old; run without retries rather than fail
            pass

    def get_artifact_summary(self, repo_paths: list) -> dict:
        """Read the security summary of artifacts Xray has ALREADY scanned.

        This does not trigger a scan. See trigger_scan() for that.

        Args:
            repo_paths: repo-relative artifact paths, in the form the Xray docs
                use, for example "docker-local/nginx/latest/manifest.json".

        Returns:
            Vulnerability summary. An empty "artifacts" array means Xray has no
            scan data for that path, NOT that the artifact is clean.
        """
        r = self._read_session.post(
            f"{self.base_url}/api/v2/summary/artifact",
            json={"paths": repo_paths},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def trigger_scan(self, component_id: str) -> dict:
        """Trigger an Xray scan of an artifact.

        Args:
            component_id: the artifact's COMPONENT ID, not a repository path.
                The API documents the form "docker://image_name:image_tag";
                other package types use their own scheme, e.g.
                "gav://group:artifact:version". Passing a repo path here is the
                most common mistake and yields nothing useful.

        Returns:
            The scan-initiation response. This call is fire-and-forget: it
            returns no scan id, so poll POST /api/v1/artifact/status for
            completion rather than looking for an id-keyed status endpoint.

        Requires the Manage Xray Metadata permission.
        """
        r = self.session.post(
            f"{self.base_url}/api/v1/scanArtifact",
            json={"componentID": component_id},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def get_scan_status(self, repo: str, path: str) -> dict:
        """Return Xray's scan status for one artifact.

        Use this to tell "scanned and clean" apart from "never scanned", which
        the summary endpoint cannot distinguish for you.
        """
        r = self._read_session.post(
            f"{self.base_url}/api/v1/artifact/status",
            json={"repo": repo, "path": path},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def list_policies(self) -> list:
        """List all security and license policies.

        Returns:
            List of policies
        """
        r = self.session.get(f"{self.base_url}/api/v2/policies", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def create_security_policy(self, name: str, rules: list) -> dict:
        """Create a security policy with CVE severity rules.

        Args:
            name: Policy name
            rules: List of rule dicts with keys: name, severity, action
                   severity: Critical, High, Medium, Low
                   action: block_download, notify, fail_build

        Returns:
            Created policy
        """
        policy_rules = []
        for i, rule in enumerate(rules, start=1):
            policy_rules.append({
                "name": rule["name"],
                # `priority` is required per rule and must be unique within the
                # policy. Omitting it makes the POST fail with 400 before any of
                # the action settings are even evaluated.
                "priority": rule.get("priority", i),
                "criteria": {
                    "min_severity": rule["severity"]
                },
                "actions": {
                    # block_download is an OBJECT with `active`; the other two
                    # are plain booleans in the v2 schema. Sending {"active":...}
                    # for notify_watch_recipients is silently wrong.
                    "block_download": {
                        "active": rule["action"] == "block_download",
                        "unscanned": rule.get("block_unscanned", False)
                    },
                    "notify_watch_recipients": rule["action"] == "notify",
                    # A rule only fails a build when this is true AND the watch
                    # carrying the policy covers the resource being scanned.
                    "fail_build": bool(rule.get("fail_build",
                                                rule["action"] == "fail_build"))
                }
            })

        r = self.session.post(
            f"{self.base_url}/api/v2/policies",
            json={
                "name": name,
                "type": "security",
                "rules": policy_rules
            },
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def list_watches(self) -> list:
        """List all watches.

        Returns:
            List of watches
        """
        r = self.session.get(f"{self.base_url}/api/v2/watches", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def create_watch(self, name: str, repos: list, policy_name: str) -> dict:
        """Create a watch to monitor repositories with a policy.

        Args:
            name: Watch name
            repos: List of repository names to monitor
            policy_name: Security policy to apply

        Returns:
            Created watch
        """
        r = self.session.post(
            f"{self.base_url}/api/v2/watches",
            json={
                "general_data": {"name": name},
                "project_resources": {
                    "resources": [
                        {"type": "repository", "name": repo}
                        for repo in repos
                    ]
                },
                "assigned_policies": [
                    {"name": policy_name, "type": "security"}
                ]
            },
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def get_violations(self, watch_name: str = None, severity: str = None,
                       limit: int = 100) -> dict:
        """Search for security violations.

        Args:
            watch_name: Filter by watch name
            severity: Filter by severity (Critical, High, Medium, Low)
            limit: Maximum number of results

        Returns:
            Violations list
        """
        filters = {"pagination": {"limit": limit, "order_by": "created"}}
        if watch_name:
            filters["filters"] = {"watch_name": watch_name}
        if severity:
            filters.setdefault("filters", {})["severity"] = severity

        r = self._read_session.post(
            f"{self.base_url}/api/v1/violations",
            json=filters,
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def generate_vulnerability_report(self, repos: list,
                                       severity_filter: str = "High") -> dict:
        """Generate a vulnerability report for repositories.

        Args:
            repos: List of repository names
            severity_filter: Minimum severity to include

        Returns:
            Report generation response (includes report ID)
        """
        r = self.session.post(
            f"{self.base_url}/api/v1/reports/vulnerabilities",
            json={
                "name": f"vuln-report-{repos[0]}",
                "resources": {
                    "repositories": [{"name": repo} for repo in repos]
                },
                "filters": {
                    "severity": [severity_filter, "Critical"]
                }
            },
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def get_report(self, report_id: str) -> dict:
        """Get report status and results.

        Args:
            report_id: Report ID from generate_vulnerability_report

        Returns:
            Report data
        """
        r = self.session.get(f"{self.base_url}/api/v1/reports/{report_id}", timeout=self.timeout)
        r.raise_for_status()
        return r.json()


def main():
    parser = argparse.ArgumentParser(
        description="JFrog Xray REST API Client"
    )
    parser.add_argument("--url", default=os.environ.get("JFROG_XRAY_URL", ""),
                        help="Xray base URL (or set JFROG_XRAY_URL env var)")
    # No --token flag on purpose: argv leaks via ps on a shared build agent.
    # The token is read from JFROG_ACCESS_TOKEN below.

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Read an existing scan result. This does NOT scan.
    sc = subparsers.add_parser(
        "summary",
        help="Read the security summary of an ALREADY-scanned artifact. Does not scan. "
             "An empty result means Xray has no data for that path, not that it is clean.")
    sc.add_argument("--path", required=True, nargs="+",
                    help="Artifact path(s), e.g. docker-local/nginx/latest/manifest.json")

    # Backwards-compatible alias for the old command name.
    sca = subparsers.add_parser("scan", help="Deprecated alias for `summary`. Does not scan.")
    sca.add_argument("--path", required=True, nargs="+", help="Artifact path(s)")

    # Actually trigger a scan.
    ts = subparsers.add_parser(
        "trigger-scan",
        help="Trigger an Xray scan. Takes a COMPONENT ID (docker://image:tag), not a repo path.")
    ts.add_argument("--component-id", required=True,
                    help="Component ID, e.g. docker://myapp:1.0.0 or gav://group:artifact:version")

    # Scan status, so 'clean' can be told apart from 'never scanned'.
    st = subparsers.add_parser("scan-status", help="Xray scan status for one artifact")
    st.add_argument("--repo", required=True, help="Repository key")
    st.add_argument("--path", required=True, help="Path within the repository")

    # Fetch a previously generated report by id.
    gr = subparsers.add_parser("get-report", help="Fetch a generated report by id")
    gr.add_argument("--report-id", required=True, help="Report id returned by `report`")

    # List policies
    subparsers.add_parser("list-policies", help="List security policies")

    # Create policy
    cp = subparsers.add_parser("create-policy", help="Create security policy")
    cp.add_argument("--name", required=True, help="Policy name")
    cp.add_argument("--block-critical", action="store_true",
                    help="Block downloads for critical CVEs")
    cp.add_argument("--block-high", action="store_true",
                    help="Block downloads for high CVEs")
    cp.add_argument("--notify-medium", action="store_true",
                    help="Notify for medium CVEs")

    # List watches
    subparsers.add_parser("list-watches", help="List watches")

    # Create watch
    cw = subparsers.add_parser("create-watch", help="Create watch")
    cw.add_argument("--name", required=True, help="Watch name")
    cw.add_argument("--repos", required=True, nargs="+",
                    help="Repositories to monitor")
    cw.add_argument("--policy", required=True, help="Policy name to apply")

    # Violations
    vl = subparsers.add_parser("violations", help="Search violations")
    vl.add_argument("--watch", help="Filter by watch name")
    vl.add_argument("--severity", choices=["Critical", "High", "Medium", "Low"],
                    help="Filter by severity")
    vl.add_argument("--limit", type=int, default=100, help="Max results")

    # Report
    rp = subparsers.add_parser("report", help="Generate vulnerability report")
    rp.add_argument("--repos", required=True, nargs="+",
                    help="Repositories to report on")
    rp.add_argument("--min-severity", default="High",
                    choices=["Critical", "High", "Medium", "Low"],
                    help="Minimum severity")

    args = parser.parse_args()

    args.token = os.environ.get("JFROG_ACCESS_TOKEN", "")

    if not args.url or not args.token:
        print("ERROR: set JFROG_XRAY_URL (or pass --url) and JFROG_ACCESS_TOKEN. "
              "The token is read from the environment only, never from argv.",
              file=sys.stderr)
        sys.exit(1)

    if not args.command:
        parser.print_help(sys.stderr)
        sys.exit(2)

    client = XrayClient(args.url, args.token)

    try:
        if args.command in ("summary", "scan"):
            if args.command == "scan":
                print("NOTE: `scan` is a deprecated alias for `summary` and does not "
                      "trigger a scan. Use `trigger-scan` for that.", file=sys.stderr)
            result = client.get_artifact_summary(args.path)
            if not result.get("artifacts"):
                print("Xray returned no scan data for that path. That is NOT the same "
                      "as clean: check the repository is under Indexed Resources and "
                      "run `scan-status` before treating this as a pass.", file=sys.stderr)
            artifacts = result.get("artifacts", [])
            for artifact in artifacts:
                general = artifact.get("general", {})
                print(f"\nArtifact: {general.get('path', 'N/A')}")
                issues = artifact.get("issues", [])
                if not issues:
                    print("  No vulnerabilities found")
                else:
                    severity_counts = {}
                    for issue in issues:
                        sev = issue.get("severity", "Unknown")
                        severity_counts[sev] = severity_counts.get(sev, 0) + 1
                    print(f"  Vulnerabilities: {len(issues)}")
                    for sev, count in sorted(severity_counts.items()):
                        print(f"    {sev}: {count}")

        elif args.command == "trigger-scan":
            print(json.dumps(client.trigger_scan(args.component_id), indent=2))

        elif args.command == "scan-status":
            print(json.dumps(client.get_scan_status(args.repo, args.path), indent=2))

        elif args.command == "get-report":
            print(json.dumps(client.get_report(args.report_id), indent=2))

        elif args.command == "list-policies":
            policies = client.list_policies()
            print(json.dumps(policies, indent=2))

        elif args.command == "create-policy":
            rules = []
            if args.block_critical:
                rules.append({"name": "block-critical",
                              "severity": "Critical", "action": "block_download"})
            if args.block_high:
                rules.append({"name": "block-high",
                              "severity": "High", "action": "block_download"})
            if args.notify_medium:
                rules.append({"name": "notify-medium",
                              "severity": "Medium", "action": "notify"})
            if not rules:
                rules = [{"name": "default-critical",
                           "severity": "Critical", "action": "block_download"}]

            result = client.create_security_policy(args.name, rules)
            print(f"Created policy: {args.name}")
            print(json.dumps(result, indent=2))

        elif args.command == "list-watches":
            watches = client.list_watches()
            print(json.dumps(watches, indent=2))

        elif args.command == "create-watch":
            result = client.create_watch(args.name, args.repos, args.policy)
            print(f"Created watch: {args.name}")
            print(json.dumps(result, indent=2))

        elif args.command == "violations":
            result = client.get_violations(
                watch_name=args.watch, severity=args.severity, limit=args.limit
            )
            violations = result.get("violations", [])
            print(f"Found {len(violations)} violations")
            for v in violations[:20]:  # Show first 20
                print(f"  [{v.get('severity', 'N/A')}] {v.get('description', 'N/A')[:80]}")

        elif args.command == "report":
            result = client.generate_vulnerability_report(
                args.repos, severity_filter=args.min_severity
            )
            print(f"Report generated: {json.dumps(result, indent=2)}")

        else:
            parser.print_help()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}",
              file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
