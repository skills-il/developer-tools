#!/usr/bin/env python3
"""JFrog Artifactory REST API Client.

A standalone client for interacting with JFrog Artifactory — supports
artifact upload/download, repository management, search (AQL), build info,
and build promotion.

Requirements:
    pip install requests

Usage:
    python artifactory_client.py --url https://mycompany.jfrog.io/artifactory \
        --token YOUR_TOKEN ping

    python artifactory_client.py --url https://mycompany.jfrog.io/artifactory \
        --token YOUR_TOKEN list-repos

    python artifactory_client.py --url https://mycompany.jfrog.io/artifactory \
        --token YOUR_TOKEN upload --repo libs-release-local \
        --path com/myapp/1.0/app.jar --file ./app.jar

    python artifactory_client.py --url https://mycompany.jfrog.io/artifactory \
        --token YOUR_TOKEN search --aql 'items.find({"repo":"libs-release-local"})'

Environment variables:
    JFROG_URL: Artifactory base URL
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


class ArtifactoryClient:
    """Client for JFrog Artifactory REST API."""

    def __init__(self, base_url: str, access_token: str):
        """Initialize Artifactory client.

        Args:
            base_url: Artifactory base URL (e.g., https://mycompany.jfrog.io/artifactory)
            access_token: JFrog access token
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def ping(self) -> bool:
        """Health check - verify connection to Artifactory.

        Returns:
            True if Artifactory is reachable
        """
        r = self.session.get(f"{self.base_url}/api/system/ping")
        return r.text.strip() == "OK"

    def version(self) -> dict:
        """Get Artifactory version information.

        Returns:
            Version info dictionary
        """
        r = self.session.get(f"{self.base_url}/api/system/version")
        r.raise_for_status()
        return r.json()

    def storage_info(self) -> dict:
        """Get storage summary.

        Returns:
            Storage information dictionary
        """
        r = self.session.get(f"{self.base_url}/api/storageinfo")
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
        r = self.session.get(f"{self.base_url}/api/repositories", params=params)
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
            json=config
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
                headers={"Content-Type": "application/octet-stream"}
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
        r = self.session.get(f"{self.base_url}/{repo_key}/{path}", stream=True)
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
        r = self.session.delete(f"{self.base_url}/{repo_key}/{path}")
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
            headers={"Content-Type": "text/plain"}
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
        r = self.session.get(f"{self.base_url}/api/search/artifact", params=params)
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
            f"{self.base_url}/api/storage/{repo_key}/{path}?properties"
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
            f"{self.base_url}/api/storage/{repo_key}/{path}?properties={prop_str}"
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
            f"{self.base_url}/api/build/{build_name}/{build_number}"
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
        r = self.session.get(f"{self.base_url}/api/build/{build_name}")
        r.raise_for_status()
        return r.json()

    def promote_build(self, build_name: str, build_number: str,
                      target_repo: str, status: str = "released",
                      copy: bool = False) -> dict:
        """Promote a build to a target repository.

        Args:
            build_name: Build name
            build_number: Build number
            target_repo: Target repository for promotion
            status: Build status after promotion
            copy: If True, copy artifacts; if False, move them

        Returns:
            Promotion response
        """
        r = self.session.post(
            f"{self.base_url}/api/build/promote/{build_name}/{build_number}",
            json={
                "status": status,
                "targetRepo": target_repo,
                "copy": copy,
                "artifacts": True,
                "dependencies": False
            }
        )
        r.raise_for_status()
        return r.json()


def main():
    parser = argparse.ArgumentParser(
        description="JFrog Artifactory REST API Client"
    )
    parser.add_argument("--url", default=os.environ.get("JFROG_URL", ""),
                        help="Artifactory base URL (or set JFROG_URL env var)")
    parser.add_argument("--token", default=os.environ.get("JFROG_ACCESS_TOKEN", ""),
                        help="Access token (or set JFROG_ACCESS_TOKEN env var)")

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
    pr.add_argument("--copy", action="store_true", help="Copy instead of move")

    args = parser.parse_args()

    if not args.url or not args.token:
        print("ERROR: --url and --token required (or set JFROG_URL and "
              "JFROG_ACCESS_TOKEN environment variables)", file=sys.stderr)
        sys.exit(1)

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
                status=args.status, copy=args.copy
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
