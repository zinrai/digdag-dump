#!/usr/bin/env python3
"""
Fetch all records of various Digdag resources via the Web API
and save them as JSON files.

Implemented using only Python 3 standard library modules.

Target resources (--resource):
  projects   GET /api/projects   (last_id + count)
  workflows  GET /api/workflows  (last_id + count)
  sessions   GET /api/sessions   (last_id + page_size)
  attempts   GET /api/attempts   (last_id + page_size)
  schedules  GET /api/schedules  (last_id + page_size)

Examples:
  $ python3 digdag_dump.py --resource projects
  $ python3 digdag_dump.py --url http://digdag:65432 --resource sessions
  $ python3 digdag_dump.py --count 200 --resource attempts
  $ python3 digdag_dump.py --limit 0 --resource sessions   # no limit (fetch all)
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from argparse import ArgumentParser


# -- Per-API configuration ----------------------------------------------------
# key_name  : key in the response JSON that holds the list of records
# size_param: query parameter name for page size
ENDPOINTS = {
    "projects": {
        "path": "/api/projects",
        "key_name": "projects",
        "size_param": "count",
    },
    "workflows": {
        "path": "/api/workflows",
        "key_name": "workflows",
        "size_param": "count",
    },
    "sessions": {
        "path": "/api/sessions",
        "key_name": "sessions",
        "size_param": "page_size",
    },
    "attempts": {
        "path": "/api/attempts",
        "key_name": "attempts",
        "size_param": "page_size",
    },
    "schedules": {
        "path": "/api/schedules",
        "key_name": "schedules",
        "size_param": "page_size",
    },
}


def fetch_page(base_url, endpoint_conf, last_id=None, count=100):
    """Fetch a single page of resources."""
    params = {
        endpoint_conf["size_param"]: str(count),
    }
    if last_id is not None:
        params["last_id"] = str(last_id)

    url = f"{base_url}{endpoint_conf['path']}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return body.get(endpoint_conf["key_name"], [])


def fetch_all(base_url, endpoint_conf, count=100, limit=0):
    """Fetch all resources with pagination. Set limit=0 for no limit."""
    all_items = []
    last_id = None

    while True:
        items = fetch_page(
            base_url,
            endpoint_conf,
            last_id=last_id,
            count=count,
        )
        if not items:
            break

        all_items.extend(items)
        last_id = items[-1]["id"]

        # Stop if the limit has been reached
        if limit > 0 and len(all_items) >= limit:
            all_items = all_items[:limit]
            break

        # Fewer items than requested means this is the last page
        if len(items) < count:
            break

        print(
            f"  fetched {len(all_items)} {endpoint_conf['key_name']} so far "
            f"(last_id={last_id})",
            file=sys.stderr,
        )

    return all_items


def main():
    parser = ArgumentParser(
        description="Fetch Digdag resources via the Web API and save as JSON",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:65432",
        help="Digdag server URL (default: http://localhost:65432)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="number of records per request (default: 100)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="maximum number of records to fetch (default: 1000, 0 for no limit)",
    )
    parser.add_argument(
        "--resource",
        required=True,
        choices=ENDPOINTS.keys(),
        help="resource to fetch (projects, workflows, sessions, attempts, schedules)",
    )

    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    endpoint_conf = ENDPOINTS[args.resource]
    output_file = f"{args.resource}_list.json"

    try:
        items = fetch_all(base_url, endpoint_conf, count=args.count, limit=args.limit)
    except urllib.error.URLError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(
        f"Total: {len(items)} {args.resource} -> {output_file}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
