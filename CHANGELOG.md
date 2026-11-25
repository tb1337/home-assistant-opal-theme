# Changelog

## Unreleased

- Screenshots of all six themes, light and dark, on a desktop and a phone, rendered from a
  demo dashboard by `script/screenshots.py`; its floor lamp shines violet to show that a
  colour light's tile glows in the light's colour.

## 1.1.0 (2026-11-25)

- Five gemstone variants next to Opal: Opal Emerald, Opal Amethyst, Opal Aquamarine, Opal
  Tourmaline and Opal Onyx, each with its own accent, a ground tinted to it and light spots
  in its tones. Opal itself is unchanged.
- `themes/opal.yaml` is now built from `src/` by `script/build.py`; the Validate workflow
  checks that it is up to date.
- Inactive states (off, clear, away) in slate instead of Home Assistant's neutral grey:
  their icons stand out from the light background, in the logbook too.
- Switches, buttons, checkboxes, radios, tabs, progress bars and pickers in Opal's
  periwinkle: they used Home Assistant's own cyan palette, which ignores `primary-color`.
- The code editor gets Opal's dark background again (the variable was renamed in Home
  Assistant).
- Removed 13 variables Home Assistant no longer reads; no visual change.

## 1.0.1 (2026-11-25)

- Changelog: 1.0.0 now reads as the first release it is. No change to the theme.

## 1.0.0 (2026-11-25)

First release.

- Frosted-glass cards, dialogs and bottom sheets, in a light and a dark mode.
- Soft coloured light (periwinkle, teal, pink) behind every page; the translucent sidebar
  lets it shine through.
- Readable form fields and opaque drop-down menus.
- With card-mod (optional): a glass header, a light sheen on cards, glowing active tiles and
  a blurred sidebar. The README lists what works with and without it.
- Listed in the Marketplace as "Opal Theme - Dark mode and light mode".
