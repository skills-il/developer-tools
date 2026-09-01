#!/usr/bin/env python3
"""JFrog Artifactory REST API Client.

A standalone client for interacting with JFrog Artifactory, supports
artifact upload/download, repository management, search (AQL), build info,
and build promotion.

Requirements:
    pip install requests

Usage:
    export JFROG_URL="https://acme.jfrog.io/artifactory"
    export JFROG_ACCESS_TOKEN="..."          # never pass a token on argv

    python3 artifactory_client.py ping
    python3 artifactory_client.py list-repos
    python3 artifactory_client.py upload --repo libs-release-local \
        --path com/myapp/1.0/app.jar --file ./app.jar
    python3 artifactory_client.py search --aql 'items.find({"repo":"libs-release-local"}).limit(100)'

Environment variables:
    JFROG_URL: Artifactory base URL
    JFROG_ACCESS_TOKEN: Access token for authentication

The token is read from the environment only. It is deliberately NOT accepted as a
command-line flag: argv is world-readable through `ps` and /proc on a shared build
agent, so a flag would leak a platform-scoped JFrog token to every user on the host.

AQL returns a bounded page, and this client does not paginate. Always put an explicit
`.limit()` in your query and read `range.total` in the response before acting on the
result, or a cleanup script will silently operate on a subset of what it matched.
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


class ArtifactoryClient:
    """Client for JFrog Artifactory REST API."""

    def __init__(self, base_url: str, access_token: str, timeout: int = 60):
        """Initialize Artifactory client.

        Args:
            base_url: Artifactory base URL (e.g., https://acme.jfrog.io/artifactory)
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
        # Retry-After. Without a retry policy a burst of calls from a CI job
        # fails on the first throttle rather than backing off.
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            retry = Retry(total=4, backoff_factor=1.5,
                          status_forcelist=(429, 500, 502, 503, 504),
                          # Only idempotent methods are retried. A PUT upload streams an
                          # open file handle, so a retry would re-send a body already at
                          # EOF against the original Content-Length: that can land a
                          # truncated artifact under a 201. POST is excluded because
                          # creating a policy or watch, or promoting a build, is not safe
                          # to repeat when the server processed the first request and only
                          # the response failed.
                          allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
                          respect_retry_after_header=True)
            self.session.mount("https://", HTTPAdapter(max_retries=retry))
            self.session.mount("http://", HTTPAdapter(max_retries=retry))
        except Exception:  # urllib3 too old; run without retries rather than fail
            pass

    def ping(self) -> bool:
        """Health check - verify connection to Artifactory.

        Returns:
            True if Artifactory is reachable
        """
        r = self.session.get(f"{self.base_url}/api/system/ping", timeout=self.timeout)
        return r.text.strip() == "OK"

    def version(self) -> dict:
        """Get Artifactory version information.

        Returns:
            Version info dictionary
        """
        r = self.session.get(f"{self.base_url}/api/system/version", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def storage_info(self) -> dict:
        """Get storage summary.

        Returns:
            Storage information dictionary
        """
        r = self.session.get(f"{self.base_url}/api/storageinfo", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def list_repos(self, repo_type: str = None) -> list:
        """List all repositories.

        Args:
            repo_type: Filter by type (local, remote, virtual, federated)

        Returns:
            List of repository dictionaries
        """
        params = {}
        if repo_type:
            params["type"] = repo_type
        r = self.session.get(f"{self.base_url}/api/repositories", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def create_repo(self, repo_key: str, repo_type: str = "local",
                    package_type: str = "generic", description: str = "") -> dict:
        """Create a new repository.

        Args:
            repo_key: Repository key/name
            repo_type: Repository type (local, remote, virtual)
            package_type: Package type (generic, maven, docker, npm, etc.)
            description: Repository description

        Returns:
            API response
        """
        config = {
            "key": repo_key,
            "rclass": repo_type,
            "packageType": package_type,
            "description": description
        }
        r = self.session.put(
            f"{self.base_url}/api/repositories/{repo_key}",
            json=config,
            timeout=self.timeout
        )
        r.raise_for_status()
        return {"status": "created", "repo": repo_key}

    def deploy_artifact(self, repo_key: str, path: str, file_path: str,
                        properties: dict = None) -> dict:
        """Deploy (upload) an artifact.

        Args:
            repo_key: Target repository key
            path: Path within repository
            file_path: Local file to upload
            properties: Optional properties to set on artifact

        Returns:
            Upload response
        """
        url = f"{self.base_url}/{repo_key}/{path}"
        if properties:
            prop_str = ";".join(f"{k}={v}" for k, v in properties.items())
            url += f";{prop_str}"

        with open(file_path, "rb") as f:
            r = self.session.put(
                url, data=f,
                headers={"Content-Type": "application/octet-stream"},
                timeout=self.timeout
            )
        r.raise_for_status()
        return r.json()

    def download_artifact(self, repo_key: str, path: str, dest_path: str) -> str:
        """Download an artifact.

        Args:
            repo_key: Source repository key
            path: Path within repository
            dest_path: Local destination path

        Returns:
            Destination path
        """
        r = self.session.get(f"{self.base_url}/{repo_key}/{path}", stream=True, timeout=self.timeout)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest_path

    def delete_artifact(self, repo_key: str, path: str) -> bool:
        """Delete an artifact.

        Args:
            repo_key: Repository key
            path: Path within repository

        Returns:
            True if deleted
        """
        r = self.session.delete(f"{self.base_url}/{repo_key}/{path}", timeout=self.timeout)
        r.raise_for_status()
        return True

    def search_aql(self, aql_query: str) -> dict:
        """Search using Artifactory Query Language.

        Args:
            aql_query: AQL query string

        Returns:
            Search results
        """
        r = self.session.post(
            f"{self.base_url}/api/search/aql",
            data=aql_query,
            headers={"Content-Type": "text/plain"},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def search_by_name(self, name: str, repos: str = None) -> dict:
        """Quick search by artifact name.

        Args:
            name: Artifact name (supports wildcards)
            repos: Comma-separated repository list

        Returns:
            Search results
        """
        params = {"name": name}
        if repos:
            params["repos"] = repos
        r = self.session.get(f"{self.base_url}/api/search/artifact", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_artifact_properties(self, repo_key: str, path: str) -> dict:
        """Get properties of an artifact.

        Args:
            repo_key: Repository key
            path: Path within repository

        Returns:
            Properties dictionary
        """
        r = self.session.get(
            f"{self.base_url}/api/storage/{repo_key}/{path}?properties",
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def set_artifact_properties(self, repo_key: str, path: str,
                                 properties: dict) -> bool:
        """Set properties on an artifact.

        Args:
            repo_key: Repository key
            path: Path within repository
            properties: Properties to set

        Returns:
            True if set successfully
        """
        prop_str = ";".join(f"{k}={v}" for k, v in properties.items())
        r = self.session.put(
            f"{self.base_url}/api/storage/{repo_key}/{path}?properties={prop_str}",
            timeout=self.timeout
        )
        r.raise_for_status()
        return True

    def get_build_info(self, build_name: str, build_number: str) -> dict:
        """Get build information.

        Args:
            build_name: Build name
            build_number: Build number

        Returns:
            Build info dictionary
        """
        r = self.session.get(
            f"{self.base_url}/api/build/{build_name}/{build_number}",
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def list_builds(self, build_name: str) -> dict:
        """List all runs for a build.

        Args:
            build_name: Build name

        Returns:
            List of build runs
        """
        r = self.session.get(f"{self.base_url}/api/build/{build_name}", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def promote_build(self, build_name: str, build_number: str,
                      target_repo: str, status: str = "released",
                      copy: bool = True, source_repo: str = None) -> dict:
        """Promote a build to a target repository.

        Args:
            build_name: Build name
            build_number: Build number
            target_repo: Target repository for promotion
            status: Build status after promotion
            copy: True copies the artifacts (the default, and almost always what
                you want). False MOVES them out of the source repository, which
                breaks every existing resolution against that repo and is not
                undone by promoting again. Moving also requires Delete
                permission on the source, not just Deploy on the target.
            source_repo: the repository to promote FROM. Set it whenever more
                than one repository could hold the build's artifacts, otherwise
                the promotion target is ambiguous.

        Returns:
            Promotion response
        """
        payload = {
            "status": status,
            "targetRepo": target_repo,
            "copy": copy,
            "artifacts": True,
            "dependencies": False
        }
        if source_repo:
            payload["sourceRepo"] = source_repo
        r = self.session.post(
            f"{self.base_url}/api/build/promote/{build_name}/{build_number}",
            json=payload,
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()


def main():
    parser = argparse.ArgumentParser(
        description="JFrog Artifactory REST API Client"
    )
    parser.add_argument("--url", default=os.environ.get("JFROG_URL", ""),
                        help="Artifactory base URL (or set JFROG_URL env var)")
    # No --token flag on purpose: argv leaks via ps on a shared build agent.
    # The token is read from JFROG_ACCESS_TOKEN below.

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Ping
    subparsers.add_parser("ping", help="Health check")

    # Version
    subparsers.add_parser("version", help="Get version info")

    # Storage
    subparsers.add_parser("storage", help="Get storage info")

    # List repos
    lr = subparsers.add_parser("list-repos", help="List repositories")
    lr.add_argument("--type", choices=["local", "remote", "virtual", "federated"],
                    help="Filter by type")

    # Upload
    up = subparsers.add_parser("upload", help="Upload artifact")
    up.add_argument("--repo", required=True, help="Repository key")
    up.add_argument("--path", required=True, help="Path in repository")
    up.add_argument("--file", required=True, help="Local file to upload")

    # Download
    dl = subparsers.add_parser("download", help="Download artifact")
    dl.add_argument("--repo", required=True, help="Repository key")
    dl.add_argument("--path", required=True, help="Path in repository")
    dl.add_argument("--output", required=True, help="Local output path")

    # Search
    sr = subparsers.add_parser("search", help="Search artifacts")
    sr.add_argument("--aql", help="AQL query")
    sr.add_argument("--name", help="Search by name")
    sr.add_argument("--repos", help="Limit to repositories (comma-separated)")

    # Build info
    bi = subparsers.add_parser("build-info", help="Get build info")
    bi.add_argument("--name", required=True, help="Build name")
    bi.add_argument("--number", required=True, help="Build number")

    # Promote
    pr = subparsers.add_parser("promote", help="Promote build")
    pr.add_argument("--name", required=True, help="Build name")
    pr.add_argument("--number", required=True, help="Build number")
    pr.add_argument("--target-repo", required=True, help="Target repository")
    pr.add_argument("--status", default="released", help="Status after promotion")
    pr.add_argument("--move", action="store_true",
                    help="MOVE artifacts out of the source repo instead of copying. "
                         "Copying is the default; moving breaks existing resolution "
                         "against the source repo and needs Delete permission on it.")
    pr.add_argument("--source-repo", help="Repository to promote FROM (set this when "
                                          "more than one repo could hold the artifacts)")

    args = parser.parse_args()

    args.token = os.environ.get("JFROG_ACCESS_TOKEN", "")

    if not args.url or not args.token:
        print("ERROR: set JFROG_URL (or pass --url) and JFROG_ACCESS_TOKEN. "
              "The token is read from the environment only, never from argv.",
              file=sys.stderr)
        sys.exit(1)

    if not args.command:
        parser.print_help(sys.stderr)
        sys.exit(2)

    client = ArtifactoryClient(args.url, args.token)

    try:
        if args.command == "ping":
            ok = client.ping()
            print(f"Artifactory: {'OK' if ok else 'FAILED'}")
            sys.exit(0 if ok else 1)

        elif args.command == "version":
            print(json.dumps(client.version(), indent=2))

        elif args.command == "storage":
            print(json.dumps(client.storage_info(), indent=2))

        elif args.command == "list-repos":
            repos = client.list_repos(repo_type=args.type)
            print(f"{'Key':<40} {'Type':<10} {'Package':<12} {'URL'}")
            print("-" * 90)
            for repo in repos:
                print(f"{repo.get('key', 'N/A'):<40} "
                      f"{repo.get('type', 'N/A'):<10} "
                      f"{repo.get('packageType', 'N/A'):<12} "
                      f"{repo.get('url', 'N/A')}")

        elif args.command == "upload":
            result = client.deploy_artifact(args.repo, args.path, args.file)
            print(f"Uploaded: {args.file} -> {args.repo}/{args.path}")
            print(json.dumps(result, indent=2))

        elif args.command == "download":
            dest = client.download_artifact(args.repo, args.path, args.output)
            print(f"Downloaded: {args.repo}/{args.path} -> {dest}")

        elif args.command == "search":
            if args.aql:
                results = client.search_aql(args.aql)
            elif args.name:
                results = client.search_by_name(args.name, repos=args.repos)
            else:
                print("ERROR: Specify --aql or --name for search", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(results, indent=2))

        elif args.command == "build-info":
            info = client.get_build_info(args.name, args.number)
            print(json.dumps(info, indent=2))

        elif args.command == "promote":
            result = client.promote_build(
                args.name, args.number, args.target_repo,
                status=args.status, copy=not args.move,
                source_repo=args.source_repo
            )
            print(f"Promoted: {args.name}/{args.number} -> {args.target_repo}")
            print(json.dumps(result, indent=2))

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
