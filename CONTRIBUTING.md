# Contributing

Thanks for your interest. This is a small, single-file project, so the workflow is light.

## Workflow

1. Fork and branch from `main`.
2. Make your change in `Mortgage_Dashboard.html` (and the tests/docs if relevant).
3. Run the test suite and confirm it is green (see below).
4. Open a pull request describing what changed and why.

## Running the tests

```bash
python -m pip install -r tests/requirements.txt
python -m playwright install chromium
python tests/e2e_test.py        # -> 48 / 48 passed
python tests/analyst_check.py   # -> 39 / 39 checks agree
python tests/i18n_test.py       # -> 27 / 27 passed
```

A PR should keep all three green. If you change the maths, `analyst_check.py` (which recomputes
independently) must still agree to the cent. If you change the sample inputs, update the pinned
baselines (see `docs/DEVELOPMENT.md`).

## Code style

- One file, vanilla ES5-ish JavaScript, no dependencies, no build step. Please keep it that way.
- No em dashes or en dashes anywhere (prose, code, comments). Use commas, colons, parentheses, or a
  plain hyphen.
- Percentages and monthly money show 2 decimals and are never rounded; only grand totals may round.
- German number format (`de-DE`) in both languages.
- Address displayed values by a stable `id`; keep `data-path` / `data-add` / `data-k` / `data-rk`
  attributes intact (the tests select on them).
- Match the surrounding code's naming and density.

## Localisation

Both English and German must stay in sync. For static text add a `data-i18n*` key and a `I18N_DE`
entry; for dynamic strings add a builder to both `TPL.en` and `TPL.de`. See `docs/DEVELOPMENT.md`.
German should use real finance/tax terminology, not literal translation.

## Please do not commit real personal data

The repo ships only a fictional sample property. Do not add real loan, bank, account, address, or
personal financial data to the app, the tests, the docs, or commit messages. `.gitignore` has patterns
for keeping private working files out; please keep your own actuals local.

## Reporting issues

Open a GitHub issue with steps to reproduce, the browser, and what you expected vs saw. For a maths
discrepancy, include the property inputs so it can be reproduced against `analyst_check.py`.

## License

By contributing you agree your contributions are licensed under the Apache License 2.0 (see `LICENSE`).
