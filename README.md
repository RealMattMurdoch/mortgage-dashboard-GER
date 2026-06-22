# Mortgage Dashboard

A single-file, offline mortgage and buy-to-let dashboard for the German market, with a built-in
**DE / EN** language toggle. Open one HTML file in any browser and model a property's amortisation,
overpayments (Sondertilgung), inflation-linked rent (Indexmiete), the rental tax benefit, the
follow-on financing after the fixed period (Anschlussfinanzierung), and a 10-year sale scenario.

No server, no build step, no dependencies, no network calls. Your data stays in your browser.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Offline](https://img.shields.io/badge/network-none%20(offline)-brightgreen)

> ## Disclaimer
>
> **This is a software tool, not financial, tax, or legal advice.** The author is **not** a financial
> or tax adviser. Every figure, calculation, projection, and forecast it produces is illustrative and
> may be wrong. **No responsibility or liability is accepted** for any errors or inaccuracies, or for
> any decision made on the basis of this tool. Always **seek professional advice** (for example from a
> qualified financial adviser, tax adviser, or Steuerberater) before acting. The software is provided
> "as is", without warranty of any kind (see [`LICENSE`](LICENSE) and [`DISCLAIMER.md`](DISCLAIMER.md)).
> The property shipped with the app is a fictional sample, not real data.

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
  DISCLAIMER.md               not financial/tax advice; no warranty or liability
  CONTRIBUTING.md             how to contribute
  CODE_OF_CONDUCT.md          community expectations
  docs/
    ARCHITECTURE.md           data model, engine, render layer, i18n design
    DEVELOPMENT.md            how to run, test, and extend the app
    TECH_STACK.md             tech choices and why
  private/                    git-ignored: YOUR real data goes here (see private/README.md)
  .github/                    CODEOWNERS, PR/issue templates, CI workflow
  tests/
    README.md                 how to install and run the checks
    requirements.txt
    e2e_test.py               end-to-end UI + render suite
    analyst_check.py          independent maths-accuracy harness
    i18n_test.py              DE/EN localisation suite
    fileurl_test.py           file:// (double-click) path check
    diag.py                   quick smoke test
```

## Using it with your own data (and staying private)

The repository ships only a **fictional sample**. Your real numbers stay in your browser
(`localStorage`) and never touch git. The recommended two-tier setup, which works the same for you and
for anyone who forks the tool:

1. **Public repo** (this one): the app, the sample, docs, and tests. This is what you clone and what
   pull requests target.
2. **Your own data**: keep property JSON exports (from the app's `Export` button) and personal notes in
   the **git-ignored [`private/`](private/) folder**. Nothing there is ever committed. If you customise
   the app heavily for yourself, keep that copy in a separate **private** repository, and contribute
   only generic improvements back here.

This separation means you can `git pull` new versions without your figures ever being tracked, and open
pull requests that contain only code.

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

## Accuracy and validation

The **arithmetic** is checked against independent references, not just against itself: a from-scratch
month-by-month amortiser, the textbook closed-form annuity formula, and open-source amortisers, all
reproduced to the cent in `tests/analyst_check.py`. The app uses standard German conventions (nominal
`Sollzins / 12`, monthly compounding, payments in arrears, Sondertilgung booked at the start of the year).

This validates that the maths is internally correct. It does **not** mean any result is right for your
situation. Outputs can legitimately differ from other mortgage calculators because of differing
conventions (start-of-year vs end-of-year overpayments, day-count, rounding, or how the effective rate
folds in fees), and a difference does not by itself mean either tool is wrong. This project does not
claim to match, replace, or be endorsed by any other named product or service. See
[`DISCLAIMER.md`](DISCLAIMER.md).

## Contributing

Got an idea to make this more useful? Found a bug, or a number that looks off? Contributions are very
welcome. Open an issue to start a conversation, or send a pull request.

Pull requests are the way changes get in. **Anyone can contribute, and every pull request is reviewed
and approved by the owner ([@RealMattMurdoch](https://github.com/RealMattMurdoch)) before it is
merged** (no direct pushes to `main`). A CI workflow runs the full test suite on each pull request, so
please make sure the tests are green locally first.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow and code style, and
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) for community expectations. Please never include real
personal financial data in a contribution.

## Philosophy

This is a small tool built for a simple reason: to help people understand a large financial commitment
honestly and make calmer decisions about it. In that spirit it takes no data (no network calls, no
analytics, no accounts), it is honest about what is an estimate versus a fact, and it is free to use,
read, and build on. If you extend it, please keep it useful and kind, and keep it from harming the
people who rely on it.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - how the app is built (read before changing it).
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - run, test, and extend it.
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md) - the stack and the reasoning behind it.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - contribution workflow and code style.
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) - community expectations.
- [`DISCLAIMER.md`](DISCLAIMER.md) - not financial/tax advice; no warranty or liability.

## Author

Built by **RealMattMurdoch**.

- GitHub: https://github.com/RealMattMurdoch
- LinkedIn: https://www.linkedin.com/in/matthewmurdoch/

## License

Apache License 2.0. See [`LICENSE`](LICENSE). The software is provided "as is", without warranty of
any kind (LICENSE sections 7 and 8 disclaim warranty and limit liability), and is **not financial or
tax advice**. See [`DISCLAIMER.md`](DISCLAIMER.md).
