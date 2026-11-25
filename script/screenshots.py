#!/usr/bin/env python3
"""Render the README's screenshots from docs/demo/dashboard.html.

For every theme in src/variants.yaml, in light and dark mode, on a phone and a desktop,
the demo page gets that theme's colours as CSS variables and is saved as
docs/screenshots/<slug>-<device>-<mode>.webp. They are previews of a demo page in the
theme's colours, not captures of Home Assistant.

Needs Playwright with Chromium and Pillow (and PyYAML); the page loads Inter and Space
Grotesk from Google Fonts. Usage: script/screenshots.py [slug ...]
"""

import io
import sys
from pathlib import Path

import yaml
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "demo" / "dashboard.html"
VARIANTS = ROOT / "src" / "variants.yaml"
OUT = ROOT / "docs" / "screenshots"

DEVICES = {
    "mobile": {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2},
    "desktop": {"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
}

# The light spots' strength per mode, as in src/theme.template.yaml.
SPOT_ALPHA = {"light": (0.45, 0.30, 0.26), "dark": (0.50, 0.34, 0.28)}

FIXED = {
    "light": {
        "--text": "#0F172A",
        "--text2": "#475569",
        "--card": "rgba(255, 255, 255, 0.55)",
        "--card-sheen": "linear-gradient(135deg, rgba(255, 255, 255, 0.55) 0%, rgba(255, 255, 255, 0.10) 60%)",
        "--card-border": "rgba(255, 255, 255, 0.75)",
        "--card-shadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
        "--header-border": "rgba(15, 23, 42, 0.06)",
        "--sidebar-text": "#334155",
        "--divider": "rgba(15, 23, 42, 0.10)",
        "--icon": "#475569",
        "--icon-bg": "rgba(15, 23, 42, 0.06)",
        "--active": "#F59E0B",
        "--inactive": "#64748B",
        "--track": "rgba(15, 23, 42, 0.10)",
        "--chip": "rgba(255, 255, 255, 0.60)",
        "--chip-border": "rgba(255, 255, 255, 0.80)",
        "--check": "rgba(15, 23, 42, 0.30)",
        "--switch-off": "rgba(15, 23, 42, 0.05)",
    },
    "dark": {
        "--text": "rgba(255, 255, 255, 0.92)",
        "--text2": "rgba(255, 255, 255, 0.66)",
        "--card": "rgba(255, 255, 255, 0.08)",
        "--card-sheen": "linear-gradient(135deg, rgba(255, 255, 255, 0.09) 0%, rgba(255, 255, 255, 0.015) 55%)",
        "--card-border": "rgba(255, 255, 255, 0.09)",
        "--card-shadow": "0 10px 30px rgba(0, 0, 0, 0.22)",
        "--header-border": "rgba(255, 255, 255, 0.07)",
        "--sidebar-text": "rgba(255, 255, 255, 0.78)",
        "--divider": "rgba(255, 255, 255, 0.12)",
        "--icon": "rgba(255, 255, 255, 0.70)",
        "--icon-bg": "rgba(255, 255, 255, 0.08)",
        "--active": "#FBBF24",
        "--inactive": "#94A3B8",
        "--track": "rgba(255, 255, 255, 0.12)",
        "--chip": "rgba(255, 255, 255, 0.08)",
        "--chip-border": "rgba(255, 255, 255, 0.12)",
        "--check": "rgba(255, 255, 255, 0.28)",
        "--switch-off": "rgba(255, 255, 255, 0.07)",
    },
}


def css_vars(variant: dict, mode: str) -> dict:
    """The demo page's variables for one theme and mode."""
    m = variant[mode]
    a1, a2, a3 = SPOT_ALPHA[mode]
    bg = (
        f"radial-gradient(circle at 8% 0%, rgba({m['spot1']}, {a1}) 0%, rgba({m['spot1']}, 0) 45%), "
        f"radial-gradient(circle at 96% 42%, rgba({m['spot2']}, {a2}) 0%, rgba({m['spot2']}, 0) 40%), "
        f"radial-gradient(circle at 42% 108%, rgba({m['spot3']}, {a3}) 0%, rgba({m['spot3']}, 0) 42%), "
        f"{m['ground']}"
    )
    palette = variant["palette"]
    header_rgb = m["ground_rgb"] if mode == "light" else m["header_rgb"]
    out = dict(FIXED[mode])
    out.update({
        "--primary": m["primary"],
        "--bg": bg,
        "--header": f"rgba({header_rgb}, 0.86)",
        "--sidebar": f"rgba({m['sidebar_rgb']}, 0.5)",
        "--loud": palette["40"],
        "--on": palette["40"] if mode == "light" else palette["60"],
        "--fill": palette["90"] if mode == "light" else palette["10"],
    })
    return out


def main() -> int:
    variants = yaml.safe_load(VARIANTS.read_text(encoding="utf-8"))
    wanted = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for device, options in DEVICES.items():
            page = browser.new_page(**options)
            page.goto(PAGE.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(1500)
            for variant in variants:
                if wanted and variant["slug"] not in wanted:
                    continue
                for mode in ("light", "dark"):
                    page.evaluate(
                        "([device, vars]) => { document.body.className = device;"
                        " for (const [k, v] of Object.entries(vars)) document.documentElement.style.setProperty(k, v); }",
                        [device, css_vars(variant, mode)],
                    )
                    page.wait_for_timeout(300)
                    png = page.screenshot(full_page=False)
                    target = OUT / f"{variant['slug']}-{device}-{mode}.webp"
                    Image.open(io.BytesIO(png)).save(target, "WEBP", quality=82, method=6)
                    print(f"wrote {target.relative_to(ROOT)}")
            page.close()
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
