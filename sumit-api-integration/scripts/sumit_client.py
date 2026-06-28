#!/usr/bin/env python3
"""Minimal, zero-dependency client for the SUMIT (OfficeGuy) REST API.

Wraps the SUMIT request convention so callers do not repeat boilerplate:
  - injects the Credentials object (CompanyID + APIKey) into every body
  - POSTs JSON to https://api.sumit.co.il/<path>
  - raises on a non-Success Status, even when HTTP is 200

Credentials are read from environment variables. Nothing is hardcoded:
  SUMIT_COMPANY_ID   your numeric company id
  SUMIT_API_KEY      your secret API key (server-side only)

Usage:
  First set SUMIT_COMPANY_ID and SUMIT_API_KEY as environment variables, then:
  python scripts/sumit_client.py --path /accounting/documents/list/ \
      --body '{"DocumentTypes":["InvoiceAndReceipt"],"Paging":{"StartIndex":0,"PageSize":50}}'
  python scripts/sumit_client.py --path /accounting/documents/list/ --body-file body.json
  python scripts/sumit_client.py --help

Uses only the Python standard library (urllib). No pip install needed.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.sumit.co.il"


class SumitError(Exception):
    """Raised when SUMIT returns a non-Success Status."""


def load_credentials():
    """Read CompanyID and the secret key from the environment."""
    company_id = os.environ.get("SUMIT_COMPANY_ID", "").strip()
    secret = os.environ.get("SUMIT_API_KEY", "").strip()
    if not company_id or not secret:
        raise SystemExit(
            "Missing credentials. Set SUMIT_COMPANY_ID and SUMIT_API_KEY "
            "in the environment before running."
        )
    return {"CompanyID": int(company_id), "APIKey": secret}


def call_sumit(path, payload, credentials=None, language="he-IL", timeout=30):
    """POST a JSON body to a SUMIT endpoint and return the Data object.

    The Credentials object is merged into the payload automatically.
    Raises SumitError if the response Status is not Success.
    """
    creds = credentials or load_credentials()
    body = dict(payload or {})
    body["Credentials"] = creds

    url = BASE_URL + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    if language:
        req.add_header("Content-Language", language)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise SumitError("Network error reaching SUMIT: " + str(exc.reason))

    try:
        parsed = json.loads(raw)
    except ValueError:
        raise SumitError("Non-JSON response from SUMIT: " + raw[:300])

    status = str(parsed.get("Status", ""))
    if not status.startswith("Success"):
        message = (
            parsed.get("UserErrorMessage")
            or parsed.get("TechnicalErrorDetails")
            or "unknown error"
        )
        raise SumitError("SUMIT " + status + ": " + str(message))
    return parsed.get("Data")


def _read_body(args):
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    if args.body:
        return json.loads(args.body)
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="Call a SUMIT (OfficeGuy) API endpoint with the Credentials envelope handled for you.",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Endpoint path, for example /accounting/documents/list/",
    )
    parser.add_argument(
        "--body",
        default="",
        help="Request body as an inline JSON string (without Credentials).",
    )
    parser.add_argument(
        "--body-file",
        default="",
        help="Path to a JSON file holding the request body (without Credentials).",
    )
    parser.add_argument(
        "--language",
        default="he-IL",
        help="Content-Language header value (default he-IL).",
    )
    args = parser.parse_args()

    try:
        payload = _read_body(args)
        data = call_sumit(args.path, payload, language=args.language)
    except SumitError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print("ERROR: invalid JSON body: " + str(exc), file=sys.stderr)
        sys.exit(2)

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
