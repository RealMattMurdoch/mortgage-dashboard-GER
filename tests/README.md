# Test suite

How to install the prerequisites and run the automated checks for the Mortgage Dashboard. The app is a
single offline HTML file (vanilla JS, no build step). The tests drive it in a real headless browser
(Chromium via Playwright) and verify the maths, the rendered numbers, the multi-property flows, the
DE/EN localisation, and that it works when opened directly from disk.

## What each script covers

| Script | What it does | Server? |
|--------|--------------|---------|
| `e2e_test.py` | End-to-end suite (48 checks): runs the in-app self-tests, verifies the sample property renders its baseline numbers (incl. Sollzins and derived Effektivzins), adds a property via the wizard, checks property-switch isolation, dated cost edits, the one-off Sondertilgung and follow-on rate projection flows, the edit-panel completeness audit and a remortgage edit, JSON export/import round-trip, and delete. Also asserts the 2-decimal formatting. | Yes (auto) |
| `analyst_check.py` | Maths-accuracy harness (39 checks). Re-computes the maths independently, both with a from-scratch Python month-by-month amortiser and with pure closed-form annuity formulae, then compares to the app engine (exposed as `window.MD_ENGINE` under `?test`) across a matrix of current and follow-on rates, overpayments, one-offs and manual payments. Expected vs actual must agree to the cent. | Yes (auto) |
| `i18n_test.py` | Localisation suite (27 checks). Confirms the app starts in English, the DE/EN toggle swaps every layer to German (tabs, hero, dynamic sentence builders, wizard, manage panel) with proper finance terminology, the choice persists across reload, switching back restores English, the `de-DE` number format stays on both sides, the `data-path` / `data-add` hooks survive translation, and no console error is thrown. | Yes (auto) |
| `fileurl_test.py` | Opens the app via a `file://` URL (the double-click case) in bundled Chromium, and your installed Chrome / Brave if present. Confirms `localStorage` persists across reload with zero console errors. | No (tests `file://`) |
| `diag.py` | Quick smoke test: loads `?test`, prints whether the app rendered and any console/page messages. Run this first if something looks broken. | Yes (auto) |

The server-based scripts serve the repo folder over `http://127.0.0.1` on a random free port, because
browsers restrict `localStorage` on `file://` in some contexts. `fileurl_test.py` deliberately tests
the raw `file://` path instead, to prove the double-click experience works.

## Prerequisites

1. **Python 3** (developed on 3.14):
   ```bash
   python --version
   ```
2. **Playwright** Python package, then the Chromium browser:
   ```bash
   python -m pip install -r requirements.txt
   python -m playwright install chromium
   ```

## Run

From the repo root:

```bash
python tests/e2e_test.py        # -> 48 / 48 passed
python tests/analyst_check.py   # -> 39 / 39 checks agree
python tests/i18n_test.py       # -> 27 / 27 passed
python tests/fileurl_test.py
python tests/diag.py
```

The scripts locate the app relative to their own folder, so they keep working if the repo is moved.

## In-app self-tests

Open `Mortgage_Dashboard.html?test` in a browser. A panel runs the engine unit checks (amortisation,
refi payment, tax, sale, one-off events, rate projection, closed-form balance cross-checks at several
rates, a negative-amortisation guard, and the Effektivzins-is-derived check) and reports `X / Y passed`.

The sample property is fictional, so its numeric baselines are the engine's own output and act as
regression pins. The real correctness proofs are the closed-form cross-check (a pure annuity formula,
independent of the iterative engine) and `analyst_check.py`.
