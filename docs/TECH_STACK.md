# Tech stack

A deliberately small stack. The whole product is one file; the only tooling is for testing.

## Runtime (the app)

| Layer | Choice | Why |
|-------|--------|-----|
| Markup | Plain HTML5, one file | Double-click to run. Nothing to install or build. |
| Styling | Hand-written CSS in a `<style>` block | No framework needed for a single dense dashboard. CSS variables for theming. |
| Logic | Vanilla JavaScript (ES5-ish), one IIFE | Runs in any browser with no transpile step; stays readable without tooling. No framework, no bundler, no dependencies. |
| Charts | Hand-drawn on `<canvas>`, `devicePixelRatio`-aware | No chart library, so no CDN or bundle. Full control over tooltips and retina sharpness. |
| State | Browser `localStorage` | Per-property persistence with zero backend. |
| Network | None | No fetch/XHR, no analytics, no fonts/CDNs. Privacy by construction and works fully offline. |
| i18n | Custom DE/EN layer (dictionary + locale-aware builders) | See ARCHITECTURE.md section 8. No i18n library. |

Design constraints that follow from "one offline file": no external assets, no build artifacts, and
everything (CSS, JS, copy, both languages) lives in `Mortgage_Dashboard.html`.

## Tooling (tests only)

| Tool | Version | Use |
|------|---------|-----|
| Python | 3.x | Runs the test harnesses and a throwaway local HTTP server. |
| Playwright | see `tests/requirements.txt` | Drives headless Chromium to render the app and assert behaviour. |
| Chromium | installed via `python -m playwright install chromium` | The browser the tests run in. |

The tests are the only thing that needs installing, and only if you want to run the suite. The app
itself has no toolchain.

## Browser support

Any modern evergreen browser (Chromium, Firefox, Safari). The code is intentionally ES5-ish and avoids
exotic APIs. `localStorage` is required for persistence; on the `file://` double-click path this works
in current Chromium-based browsers (covered by `tests/fileurl_test.py`).

## What is intentionally NOT here

- No build step, package manager, or `node_modules`.
- No runtime dependencies or CDNs.
- No server, database, or accounts.
- No telemetry or network calls of any kind.
