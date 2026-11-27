#!/usr/bin/env python3
"""Take the README's screenshots of a dashboard in a running Home Assistant.

For every theme in src/variants.yaml, in light and dark mode, on a phone and a desktop, the
dashboard is opened with that theme selected in the browser (the user's profile is not
changed) and saved as docs/screenshots/<slug>-<device>-<mode>.webp. Opal and card-mod must be
installed in that Home Assistant.

Needs Playwright with Chromium, Pillow and PyYAML. The login is a long-lived access token in
HA_TOKEN; it is never printed.

Usage: HA_URL=https://ha.example HA_TOKEN=... script/screenshots.py /dashboard/view [slug ...]
"""

import io
import json
import os
import sys
from pathlib import Path

import yaml
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = ROOT / "src" / "variants.yaml"
OUT = ROOT / "docs" / "screenshots"

DEVICES = {
    "mobile": {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2,
               "is_mobile": True, "has_touch": True},
    "desktop": {"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
}

# Time for the dashboard, card-mod and the charts to settle.
SETTLE_MS = 8000


def login_script(base: str, token: str, theme: str, dark: bool) -> str:
    """Put the token and the theme into the page's storage before Home Assistant starts."""
    tokens = {"access_token": token, "token_type": "Bearer", "expires_in": 1800,
              "hassUrl": base, "clientId": base + "/", "refresh_token": ""}
    selected = {"theme": theme, "dark": dark}
    return (
        f"(() => {{ const t = {json.dumps(tokens)}; t.expires = Date.now() + 3600000;"
        " localStorage.setItem('hassTokens', JSON.stringify(t));"
        f" localStorage.setItem('selectedTheme', JSON.stringify({json.dumps(selected)})); }})()"
    )


def main() -> int:
    if len(sys.argv) < 2 or "HA_URL" not in os.environ or "HA_TOKEN" not in os.environ:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    base = os.environ["HA_URL"].rstrip("/")
    token = os.environ["HA_TOKEN"]
    path, wanted = sys.argv[1], set(sys.argv[2:])
    variants = yaml.safe_load(VARIANTS.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for variant in variants:
            if wanted and variant["slug"] not in wanted:
                continue
            for device, options in DEVICES.items():
                for mode in ("light", "dark"):
                    context = browser.new_context(color_scheme=mode, **options)
                    context.add_init_script(login_script(base, token, variant["name"], mode == "dark"))
                    page = context.new_page()
                    page.goto(base + path, wait_until="networkidle")
                    page.wait_for_timeout(SETTLE_MS)
                    png = page.screenshot()
                    target = OUT / f"{variant['slug']}-{device}-{mode}.webp"
                    Image.open(io.BytesIO(png)).save(target, "WEBP", quality=82, method=6)
                    print(f"wrote {target.relative_to(ROOT)}")
                    context.close()
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
