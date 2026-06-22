# Mortgage Dashboard

A single-file, offline mortgage and buy-to-let dashboard for the German market, with a built-in
**DE / EN** language toggle. Open one HTML file in any browser and model a property's amortisation,
overpayments (Sondertilgung), inflation-linked rent (Indexmiete), the rental tax benefit, the
follow-on financing after the fixed period (Anschlussfinanzierung), and a 10-year sale scenario.

No server, no build step, no dependencies, no network calls. Your data stays in your browser.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Offline](https://img.shields.io/badge/network-none%20(offline)-brightgreen)

> **Not financial or tax advice.** Every number is a planning estimate, and the property shipped
> with the app is a fictional sample. Confirm anything that matters with a qualified advisor or
> Steuerberater.

---

## Quick start

1. Download [`Mortgage_Dashboard.html`](Mortgage_Dashboard.html) (or clone the repo).
2. Double-click it. That is the whole install.

```bash
git clone https://github.com/RealMattMurdoch/mortgage-dashboard.git
cd mortgage-dashboard
# then open Mortgage_Dashboard.html in your browser
```

On first run it seeds a fictional **"Sample apartment"** so every chart and table is populated.
Edit it via **Edit values**, add your own property with the **+ Add property** wizard, or delete
the sample once you have your own. Everything is stored per-property in `localStorage` on your device.

## Features

- **Multi-property:** add, edit, switch, delete, and export/import properties as JSON.
- **Setup wizard:** a 7-step guided flow to enter a new property.
- **Amortisation engine:** month-by-month, German convention (nominal `Sollzins / 12`, monthly
  compounding, payments in arrears). Nominal rate in, effective rate (`Effektivzins`) derived as output.
- **Sondertilgung simulator:** recurring annual overpayments plus dated one-off lump sums, with an
  A/B comparison of interest saved and years shaved off, and an allowance-cap warning.
- **Two rate periods:** models the fixed period (`Sollzinsbindung`) and the follow-on
  (`Anschlussfinanzierung`) as an explicit, editable projection, with a good-vs-worse scenario table.
- **Rental tax view:** rental income vs deductible costs (`Werbungskosten`), the loss-driven tax
  saving at your marginal rate, AfA, the 15% renovation limit, and German case-law notes.
- **10-year sale scenario:** appreciation slider, equity build-up, and the breakdown of where the
  sale proceeds go, framed around the German 10-year tax-free holding rule (`§23 EStG`).
- **DE / EN toggle:** the whole UI, including the wizard and edit panel, switches between English and
  proper German finance terminology (not literal translation). Choice persists across reloads.
- **Interactive charts:** Canvas charts that are `devicePixelRatio`-aware, with hover/tap tooltips and
  a screen-reader table mirroring every chart.
- **Privacy by construction:** no network requests, no analytics, no accounts. Data never leaves the
  browser.

## Conventions

- German number format throughout (comma decimals, dot thousands), in both languages, because the
  domain is German housing finance.
- Percentages and monthly money show 2 decimals and are never rounded; only grand totals may round.

## Tech stack

Plain HTML, CSS, and vanilla ES5-ish JavaScript in one file (one IIFE, no framework, no bundler).
Charts are hand-drawn on `<canvas>`. State is browser `localStorage`. The test suite is Python +
Playwright (headless Chromium). See [`docs/TECH_STACK.md`](docs/TECH_STACK.md) for the rationale.

## Project structure

```
mortgage-dashboard/
  Mortgage_Dashboard.html     the entire app (open this)
  README.md                   this file
  LICENSE / NOTICE            Apache-2.0
  CONTRIBUTING.md             how to contribute
  docs/
    ARCHITECTURE.md           data model, engine, render layer, i18n design
    DEVELOPMENT.md            how to run, test, and extend the app
    TECH_STACK.md             tech choices and why
  tests/
    README.md                 how to install and run the checks
    requirements.txt
    e2e_test.py               end-to-end UI + render suite
    analyst_check.py          independent maths-accuracy harness
    i18n_test.py              DE/EN localisation suite
    fileurl_test.py           file:// (double-click) path check
    diag.py                   quick smoke test
```

## Testing

```bash
python -m pip install -r tests/requirements.txt
python -m playwright install chromium
python tests/e2e_test.py        # end-to-end UI + render        -> 48 / 48
python tests/analyst_check.py   # independent maths accuracy    -> 39 / 39
python tests/i18n_test.py       # DE/EN localisation            -> 27 / 27
```

You can also open `Mortgage_Dashboard.html?test` in a browser to run the in-app engine self-tests.
More detail in [`tests/README.md`](tests/README.md).

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - how the app is built (read before changing it).
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - run, test, and extend it.
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md) - the stack and the reasoning behind it.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - contribution workflow and code style.

## Author

Built by **RealMattMurdoch**.

- GitHub: https://github.com/RealMattMurdoch
- LinkedIn: https://www.linkedin.com/in/matthewmurdoch/

## License

Apache License 2.0. See [`LICENSE`](LICENSE). The software is provided "as is", without warranty of
any kind, and is not financial or tax advice.
