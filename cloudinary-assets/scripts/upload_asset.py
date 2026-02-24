#!/usr/bin/env python3
"""Cloudinary Asset Upload and Management Client.

A standalone client for uploading, transforming, and managing media assets
through Cloudinary's REST API. Supports image/video upload, URL-based
transformations, responsive image generation, and asset management.

Requirements:
    pip install requests

Usage:
    python upload_asset.py upload --file ./photo.jpg --folder products --tags "hero,main"
    python upload_asset.py transform --public-id products/photo --width 800 --height 600
    python upload_asset.py responsive --public-id products/photo
    python upload_asset.py list --type image --max 30
    python upload_asset.py delete --public-id products/photo

Environment variables:
    CLOUDINARY_URL: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
    -- or --
    CLOUDINARY_CLOUD_NAME: Cloud name
    CLOUDINARY_API_KEY: API key
    CLOUDINARY_API_SECRET: API secret
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.parse

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests",
          file=sys.stderr)
    sys.exit(1)


def get_cloudinary_config() -> dict:
    """Get Cloudinary configuration from environment variables.

    Returns:
        Dictionary with cloud_name, api_key, api_secret
    """
    # Option 1: CLOUDINARY_URL
    cloudinary_url = os.environ.get('CLOUDINARY_URL')
    if cloudinary_url:
        # Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
        parsed = urllib.parse.urlparse(cloudinary_url)
        return {
            "cloud_name": parsed.hostname,
            "api_key": parsed.username,
            "api_secret": parsed.password,
        }

    # Option 2: Individual variables
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if all([cloud_name, api_key, api_secret]):
        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
        }

    return None


def generate_signature(params: dict, api_secret: str) -> str:
    """Generate Cloudinary API signature.

    Args:
        params: Parameters to sign (sorted alphabetically)
        api_secret: Cloudinary API secret

    Returns:
        SHA1 hex signature
    """
    sorted_params = "&".join(
        f"{k}={v}" for k, v in sorted(params.items())
        if v is not None and k not in ("file", "api_key", "resource_type")
    )
    return hashlib.sha1(f"{sorted_params}{api_secret}".encode()).hexdigest()


def upload_image(file_path: str, config: dict, folder: str = "",
                 tags: list = None, public_id: str = None) -> dict:
    """Upload an image to Cloudinary.

    Args:
        file_path: Path to local file
        config: Cloudinary config dict
        folder: Optional folder in Cloudinary
        tags: Optional list of tags
        public_id: Optional custom public ID

    Returns:
        Upload response from Cloudinary
    """
    timestamp = str(int(time.time()))

    params = {"timestamp": timestamp}
    if folder:
        params["folder"] = folder
    if tags:
        params["tags"] = ",".join(tags)
    if public_id:
        params["public_id"] = public_id

    signature = generate_signature(params, config["api_secret"])

    url = f"https://api.cloudinary.com/v1_1/{config['cloud_name']}/image/upload"
    data = {
        "api_key": config["api_key"],
        "timestamp": timestamp,
        "signature": signature,
    }
    data.update({k: v for k, v in params.items() if k != "timestamp"})

    with open(file_path, "rb") as f:
        response = requests.post(url, data=data, files={"file": f})

    response.raise_for_status()
    return response.json()


def upload_video(file_path: str, config: dict, folder: str = "",
                 tags: list = None) -> dict:
    """Upload a video to Cloudinary.

    Args:
        file_path: Path to local video file
        config: Cloudinary config dict
        folder: Optional folder
        tags: Optional list of tags

    Returns:
        Upload response
    """
    timestamp = str(int(time.time()))

    params = {"timestamp": timestamp}
    if folder:
        params["folder"] = folder
    if tags:
        params["tags"] = ",".join(tags)

    signature = generate_signature(params, config["api_secret"])

    url = f"https://api.cloudinary.com/v1_1/{config['cloud_name']}/video/upload"
    data = {
        "api_key": config["api_key"],
        "timestamp": timestamp,
        "signature": signature,
    }
    data.update({k: v for k, v in params.items() if k != "timestamp"})

    with open(file_path, "rb") as f:
        response = requests.post(url, data=data, files={"file": f})

    response.raise_for_status()
    return response.json()


def build_transform_url(cloud_name: str, public_id: str,
                         transformations: dict) -> str:
    """Build a Cloudinary transformation URL.

    Args:
        cloud_name: Cloudinary cloud name
        public_id: Asset public ID
        transformations: Dict of transformation parameters

    Returns:
        Complete transformation URL
    """
    parts = []
    if "width" in transformations:
        parts.append(f"w_{transformations['width']}")
    if "height" in transformations:
        parts.append(f"h_{transformations['height']}")
    if "crop" in transformations:
        parts.append(f"c_{transformations['crop']}")
    if "gravity" in transformations:
        parts.append(f"g_{transformations['gravity']}")
    if "quality" in transformations:
        parts.append(f"q_{transformations['quality']}")
    if "format" in transformations:
        parts.append(f"f_{transformations['format']}")
    if "radius" in transformations:
        parts.append(f"r_{transformations['radius']}")
    if "effect" in transformations:
        parts.append(f"e_{transformations['effect']}")
    if "dpr" in transformations:
        parts.append(f"dpr_{transformations['dpr']}")

    transform_str = ",".join(parts) if parts else ""
    base = f"https://res.cloudinary.com/{cloud_name}/image/upload"

    if transform_str:
        return f"{base}/{transform_str}/{public_id}"
    return f"{base}/{public_id}"


def get_responsive_urls(cloud_name: str, public_id: str,
                         widths: list = None) -> dict:
    """Generate responsive image URLs for different breakpoints.

    Args:
        cloud_name: Cloudinary cloud name
        public_id: Asset public ID
        widths: List of widths for breakpoints

    Returns:
        Dictionary with urls, srcset string, and HTML snippet
    """
    if widths is None:
        widths = [320, 640, 960, 1280, 1920]

    base = f"https://res.cloudinary.com/{cloud_name}/image/upload"
    urls = {}
    for w in widths:
        urls[w] = f"{base}/w_{w},q_auto,f_auto/{public_id}"

    srcset = ", ".join(f"{url} {w}w" for w, url in urls.items())

    default_url = f"{base}/w_800,q_auto,f_auto/{public_id}"
    html = (
        f'<img\n'
        f'  src="{default_url}"\n'
        f'  srcset="{srcset}"\n'
        f'  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"\n'
        f'  alt=""\n'
        f'  loading="lazy"\n'
        f'/>'
    )

    return {"urls": urls, "srcset": srcset, "html": html}


def list_assets(config: dict, resource_type: str = "image",
                max_results: int = 30) -> dict:
    """List assets in Cloudinary media library.

    Args:
        config: Cloudinary config dict
        resource_type: Type of resource (image, video, raw)
        max_results: Maximum results to return

    Returns:
        List of assets
    """
    url = (f"https://api.cloudinary.com/v1_1/{config['cloud_name']}"
           f"/resources/{resource_type}")
    response = requests.get(
        url,
        params={"max_results": max_results},
        auth=(config["api_key"], config["api_secret"])
    )
    response.raise_for_status()
    return response.json()


def delete_asset(public_id: str, config: dict) -> dict:
    """Delete an asset from Cloudinary.

    Args:
        public_id: Asset public ID
        config: Cloudinary config dict

    Returns:
        Deletion response
    """
    timestamp = str(int(time.time()))
    params = {"public_id": public_id, "timestamp": timestamp}
    signature = generate_signature(params, config["api_secret"])

    url = f"https://api.cloudinary.com/v1_1/{config['cloud_name']}/image/destroy"
    response = requests.post(url, data={
        "public_id": public_id,
        "api_key": config["api_key"],
        "timestamp": timestamp,
        "signature": signature,
    })
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Cloudinary Asset Upload and Management Client"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Upload
    up = subparsers.add_parser("upload", help="Upload image or video")
    up.add_argument("--file", required=True, help="Local file to upload")
    up.add_argument("--folder", default="", help="Cloudinary folder")
    up.add_argument("--tags", default="", help="Comma-separated tags")
    up.add_argument("--public-id", help="Custom public ID")
    up.add_argument("--video", action="store_true", help="Upload as video")

    # Transform
    tr = subparsers.add_parser("transform", help="Generate transformation URL")
    tr.add_argument("--public-id", required=True, help="Asset public ID")
    tr.add_argument("--width", type=int, help="Width")
    tr.add_argument("--height", type=int, help="Height")
    tr.add_argument("--crop", default="fill",
                    choices=["fill", "fit", "limit", "pad", "thumb", "crop"],
                    help="Crop mode")
    tr.add_argument("--gravity", help="Gravity (face, center, auto, etc.)")
    tr.add_argument("--quality", default="auto", help="Quality (auto, 80, etc.)")
    tr.add_argument("--format", default="auto", help="Format (auto, webp, jpg, etc.)")

    # Responsive
    rs = subparsers.add_parser("responsive", help="Generate responsive image set")
    rs.add_argument("--public-id", required=True, help="Asset public ID")
    rs.add_argument("--widths", type=int, nargs="+",
                    default=[320, 640, 960, 1280, 1920],
                    help="Breakpoint widths")

    # List
    ls = subparsers.add_parser("list", help="List assets")
    ls.add_argument("--type", default="image",
                    choices=["image", "video", "raw"], help="Resource type")
    ls.add_argument("--max", type=int, default=30, help="Max results")

    # Delete
    dl = subparsers.add_parser("delete", help="Delete asset")
    dl.add_argument("--public-id", required=True, help="Asset public ID")

    args = parser.parse_args()

    config = get_cloudinary_config()
    if not config:
        print("ERROR: Cloudinary credentials not found.", file=sys.stderr)
        print("Set CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME",
              file=sys.stderr)
        print("Or set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, "
              "CLOUDINARY_API_SECRET individually.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "upload":
            tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
            if args.video:
                result = upload_video(args.file, config, folder=args.folder, tags=tags)
            else:
                result = upload_image(args.file, config, folder=args.folder,
                                       tags=tags, public_id=args.public_id)

            print(f"Uploaded: {args.file}")
            print(f"Public ID:  {result.get('public_id', 'N/A')}")
            print(f"URL:        {result.get('secure_url', 'N/A')}")
            print(f"Format:     {result.get('format', 'N/A')}")
            print(f"Size:       {result.get('bytes', 0):,} bytes")
            print(f"Dimensions: {result.get('width', 'N/A')}x{result.get('height', 'N/A')}")

            # Generate optimized URL
            opt_url = build_transform_url(
                config["cloud_name"],
                result.get("public_id", ""),
                {"quality": "auto", "format": "auto"}
            )
            print(f"\nOptimized:  {opt_url}")

        elif args.command == "transform":
            transforms = {}
            if args.width:
                transforms["width"] = args.width
            if args.height:
                transforms["height"] = args.height
            if args.crop:
                transforms["crop"] = args.crop
            if args.gravity:
                transforms["gravity"] = args.gravity
            if args.quality:
                transforms["quality"] = args.quality
            if args.format:
                transforms["format"] = args.format

            url = build_transform_url(config["cloud_name"], args.public_id, transforms)
            print(f"Transformation URL:\n{url}")

        elif args.command == "responsive":
            result = get_responsive_urls(
                config["cloud_name"], args.public_id, widths=args.widths
            )
            print("Responsive URLs:")
            for w, url in result["urls"].items():
                print(f"  {w}w: {url}")
            print(f"\nSrcset:\n{result['srcset']}")
            print(f"\nHTML:\n{result['html']}")

        elif args.command == "list":
            result = list_assets(config, resource_type=args.type, max_results=args.max)
            resources = result.get("resources", [])
            print(f"Found {len(resources)} {args.type}(s):")
            for r in resources:
                size_kb = r.get("bytes", 0) / 1024
                print(f"  {r.get('public_id', 'N/A'):<40} "
                      f"{r.get('format', 'N/A'):<6} "
                      f"{size_kb:>8.1f} KB  "
                      f"{r.get('width', '')}x{r.get('height', '')}")

        elif args.command == "delete":
            result = delete_asset(args.public_id, config)
            status = result.get("result", "unknown")
            print(f"Delete {args.public_id}: {status}")

        else:
            parser.print_help()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}",
              file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
