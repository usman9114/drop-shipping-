"""Check which country our store fetches exit from, direct and through SCOUT_PROXY.

    python -m scout.proxy_check

Prints only the two-letter country, never an IP address or credentials. Uses
Cloudflare's public trace page (https://www.cloudflare.com/cdn-cgi/trace).
"""

from __future__ import annotations

import sys

from scout import webmeta

TRACE = "https://www.cloudflare.com/cdn-cgi/trace"


def country(via_proxy: bool) -> str:
    try:
        text = webmeta._session(via_proxy).get(TRACE, timeout=20).text
    except Exception as exc:
        return f"error ({type(exc).__name__})"
    return next((ln[4:] for ln in text.splitlines() if ln.startswith("loc=")), "?")


def main() -> int:
    print("direct (your VPN app, if on):", country(False))
    if webmeta.proxy_url():
        print("through SCOUT_PROXY:        ", country(True))
    else:
        print("SCOUT_PROXY is not set in .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
