#!/usr/bin/env python3
"""JFrog Xray REST API Client.

A standalone client for interacting with JFrog Xray — supports vulnerability
scanning, security policy management, watch creation, violation search, and
report generation.

Requirements:
    pip install requests

Usage:
    python xray_client.py --url https://mycompany.jfrog.io/xray \
        --token YOUR_TOKEN scan --path "libs-release-local/com/myapp/1.0/app.jar"

    python xray_client.py --url https://mycompany.jfrog.io/xray \
        --token YOUR_TOKEN violations --watch prod-security-watch

Environment variables:
    JFROG_XRAY_URL: Xray base URL
    JFROG_ACCESS_TOKEN: Access token for authentication
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

    def __init__(self, base_url: str, access_token: str):
        """Initialize Xray client.

        Args:
            base_url: Xray base URL (e.g., https://mycompany.jfrog.io/xray)
            access_token: JFrog access token
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def get_artifact_summary(self, repo_paths: list) -> dict:
        """Get vulnerability summary for artifacts.

        Args:
            repo_paths: List of artifact paths in Artifactory

        Returns:
            Vulnerability summary
        """
        r = self.session.post(
            f"{self.base_url}/api/v2/summary/artifact",
            json={"paths": repo_paths}
        )
        r.raise_for_status()
        return r.json()

    def scan_artifact(self, repo_path: str) -> dict:
        """Trigger a scan for a specific artifact.

        Args:
            repo_path: Artifact path in Artifactory

        Returns:
            Scan initiation response
        """
        r = self.session.post(
            f"{self.base_url}/api/v1/scanArtifact",
            json={"componentId": repo_path}
        )
        r.raise_for_status()
        return r.json()

    def list_policies(self) -> list:
        """List all security and license policies.

        Returns:
            List of policies
        """
        r = self.session.get(f"{self.base_url}/api/v2/policies")
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
        for rule in rules:
            policy_rules.append({
                "name": rule["name"],
                "criteria": {
                    "min_severity": rule["severity"]
                },
                "actions": {
                    "block_download": {
                        "active": rule["action"] == "block_download"
                    },
                    "notify_watch_recipients": {
                        "active": rule["action"] == "notify"
                    },
                    "fail_build": rule.get("fail_build", False)
                }
            })

        r = self.session.post(
            f"{self.base_url}/api/v2/policies",
            json={
                "name": name,
                "type": "security",
                "rules": policy_rules
            }
        )
        r.raise_for_status()
        return r.json()

    def list_watches(self) -> list:
        """List all watches.

        Returns:
            List of watches
        """
        r = self.session.get(f"{self.base_url}/api/v2/watches")
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
            }
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

        r = self.session.post(
            f"{self.base_url}/api/v1/violations",
            json=filters
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
            }
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
        r = self.session.get(f"{self.base_url}/api/v1/reports/{report_id}")
        r.raise_for_status()
        return r.json()


def main():
    parser = argparse.ArgumentParser(
        description="JFrog Xray REST API Client"
    )
    parser.add_argument("--url", default=os.environ.get("JFROG_XRAY_URL", ""),
                        help="Xray base URL (or set JFROG_XRAY_URL env var)")
    parser.add_argument("--token", default=os.environ.get("JFROG_ACCESS_TOKEN", ""),
                        help="Access token (or set JFROG_ACCESS_TOKEN env var)")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan artifact
    sc = subparsers.add_parser("scan", help="Get vulnerability summary for artifact")
    sc.add_argument("--path", required=True, nargs="+",
                    help="Artifact path(s) in Artifactory")

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

    if not args.url or not args.token:
        print("ERROR: --url and --token required (or set JFROG_XRAY_URL and "
              "JFROG_ACCESS_TOKEN environment variables)", file=sys.stderr)
        sys.exit(1)

    client = XrayClient(args.url, args.token)

    try:
        if args.command == "scan":
            result = client.get_artifact_summary(args.path)
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
