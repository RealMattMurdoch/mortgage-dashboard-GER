# Development guide

How to run, test, and extend the app. Read [`ARCHITECTURE.md`](ARCHITECTURE.md) first for the data
model, engine, render layer, and localisation design.

## Running it

There is nothing to build. Open `Mortgage_Dashboard.html` in any browser by double-clicking it, or
serve the folder over HTTP if you prefer a real origin:

```bash
python -m http.server 8000
# then open http://127.0.0.1:8000/Mortgage_Dashboard.html
```

Append `?test` to the URL to run the in-app engine self-tests (a panel reports pass/fail and exposes
`window.MD_ENGINE` for the accuracy harness).

## Running the tests

Prerequisites: Python 3 and Playwright (Chromium).

```bash
python -m pip install -r tests/requirements.txt
python -m playwright install chromium

python tests/e2e_test.py        # end-to-end UI + render     -> 48 / 48 passed
python tests/analyst_check.py   # independent maths accuracy -> 39 / 39 checks agree
python tests/i18n_test.py       # DE/EN localisation         -> 27 / 27 passed
python tests/fileurl_test.py    # file:// double-click path
python tests/diag.py            # quick smoke test
```

After any change to the app, run at least `e2e_test.py` and `analyst_check.py` and confirm green.
The scripts locate the app relative to their own folder, so they keep working if you move the repo.

## How the code is organised

Everything lives in one `<script>` IIFE inside `Mortgage_Dashboard.html`. The order is: format
helpers, the localisation layer, series resolvers, the default/blank property, the store, the engine,
`setEngineFrom`, render functions, the wizard and manage panel, the self-tests, and `init`. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) section 3.

Two rules that the tests enforce, so keep them intact:

- Every displayed value is addressed by a stable `id` and set with `textContent` / `innerHTML`. Do not
  rename ids casually.
- The manage panel binds scalar fields by a `data-path` attribute (e.g. `data-path="loan.ratePct"`);
  dated series use `data-add` / `data-k` / `data-f` / `data-rk`. The tests select on these.

## Common changes

### Add a new editable property field

1. Add it to the property object in `sampleProperty()` and `blankProperty()`.
2. Add an input to the manage panel (`creditFields()` or the relevant card) with the right
   `data-path`. `manageSave()` walks the path and writes it back automatically.
3. If it feeds the maths, read it in `setEngineFrom()` into an engine global and use it in `amortize()`
   or the relevant model function.
4. If it should appear in the setup wizard, add a field to the matching step in `wzSteps()` and read it
   in `wzCollect()`.
5. Add or update a self-test assertion, and the matching `e2e_test.py` / `analyst_check.py` expectation.

### Change the maths

The engine is `amortize()` plus the model functions (`taxModel`, `projectYears`, `saleScenario`,
`computeSonder`, `refiPayment`). Keep full floating-point precision inside the engine; round only at
display time via the formatting helpers. Any change must keep `analyst_check.py` agreeing to the cent
(it recomputes independently with a from-scratch amortiser and closed-form annuity formulae).

### Add or change UI text

- **Static text:** put the English text in the markup and give the element a `data-i18n` key
  (`data-i18n-html` if it contains inline markup, `data-i18n-title` for a tooltip, `data-i18n-aria` for
  an aria-label). Add the German string under the same key in `I18N_DE`. English is captured from the
  DOM automatically, so you only author the German.
- **Dynamic text** (a sentence with live numbers, or wizard/manage/chart/alert strings): add a builder
  to both `TPL.en` and `TPL.de` and call it via `TL()`. Do not concatenate translated fragments; give
  each language its own full string, because word order differs.
- After adding strings, run `i18n_test.py`.

### Localisation invariants

- The number format is `de-DE` in both languages by design. Do not switch English to a different
  format.
- On a language toggle the app re-applies the static dictionary and re-renders everything; the maths is
  never affected by language. Keep it that way (no engine logic inside `TPL`/`I18N_DE`).

## Updating the sample baselines

The in-app self-tests pin a few of the sample property's engine outputs (months, payoff, balance at the
fixed end, lifetime interest, total deductions, tax saving, year-1 gap). If you change the sample's
inputs in `sampleProperty()`, recompute those outputs (the simplest way is to read them from
`window.MD_ENGINE` under `?test`, or port the amortiser as `analyst_check.py` does) and update both the
self-test constants and the `e2e_test.py` expectations. The closed-form cross-check and `analyst_check.py`
do not need updating, since they recompute from inputs.
