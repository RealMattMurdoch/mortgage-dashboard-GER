# Architecture

Read this before changing the app. It covers what the app is, why it is built the way it is, the
data model, the calculation engine, the render and localisation layers, and the test framework.

## 1. What it is

`Mortgage_Dashboard.html` is a single self-contained offline web app that models a German buy-to-let
property: mortgage amortisation, overpayment (Sondertilgung), inflation-linked rent (Indexmiete), the
rental tax benefit, the follow-on financing after the fixed period (Anschlussfinanzierung), and a
10-year sale scenario. It supports multiple properties (add, edit, delete, switch, export/import),
each stored separately in the browser, and ships with a fictional "Sample apartment" seed.

## 2. Why it is built this way (constraints)

- **Single offline HTML file.** Double-click to open. No server, no internet, no install, no build
  step, no dependencies, no CDNs. This is deliberate: the file can hold sensitive personal financial
  data, so it must work forever on any machine with a browser, with nothing to break or phone home.
- **Vanilla JavaScript** in one IIFE. No framework, no bundler. ES5-ish style so it runs anywhere and
  stays readable without tooling.
- **Privacy by construction.** All state is local (`localStorage`); the app never makes a network request.
- **Output rules:** no em dashes or en dashes anywhere; percentages and monthly money show 2 decimals
  and are never rounded; only grand totals may be rounded. German number format in both languages.

## 3. File structure (top to bottom)

The HTML is one document: `<style>` (all CSS), the markup (hero, tabs, cards, sliders, charts, wizard
drawer, manage panel), then one `<script>` IIFE with:

1. Formatting helpers
2. Localisation layer (`LOCALE`, `I18N_DE` dictionary, `TPL` locale-aware builders, `applyI18n`,
   `captureEn`, `TL()`); see section 8
3. Series resolvers (dated step-values)
4. `sampleProperty()` default + `blankProperty()`
5. Store layer (`localStorage` by id)
6. Engine state globals + the calculation engine
7. `setEngineFrom()` (activate a property)
8. Render functions (numbers, charts, screen-reader tables)
9. Setup wizard, manage/edit panel, export/import, switcher
10. In-app self-test suite (runs on `?test`)
11. Init / bootstrap

## 4. Data model

A property is a plain object (see `sampleProperty()`). Key shape:

```
{ schema, id, name, country, currency, address, loanRef, asOfMonth, asOfPayments,
  loan:{principal, ratePct (Sollzins, the only rate input; drives the maths),
        payment, startYear, fixedUntilYear, termEndYear,
        sonderMax, varRatePct, sonderEvents:[{from:'YYYY-MM', amount}]},
  // effective rate (Effektivzins) is NOT stored; it is derived for display via effAnnual()
  refinance:{ratePct, termEndYear, payment},   // phase-2 projection (defaults to current rate)
  purchase:{price, eigenkapital, purchaseCosts, condoBonus, sellCostPct,
            saleYears, notaryDate, taxFreeFrom},
  costs:{ hausgeld:[{from:'YYYY-MM', value}], sev:[{from, value}] },
  rent:{ firstMonth, firstFullStepYear, explicit:[{from, cold, warm, bk, hk}] },
  tax:{ marginalPct, dedInterest, dedAfa, dedHausgeld, dedSev, dedGrundsteuer,
        dedOther, dedFinancingOneOff, renoLimit, renoWindow },
  assumptions:{ idxPct, apprPct, sonderAnnual, refiPct },
  reno:{spent}, facts:[[label,value]...], contractTable:[{y,i,p,b}...]|null }
```

**Dated step-series.** Costs and rent are arrays of `{from, value}` entries, so a change (a Hausgeld
rise, a new rent) applies from a chosen month onward. Resolvers: `valueAt`, `seriesGrownForYear`,
`rentGrownForYear`.

**Storage keys** (`localStorage`): `mpd:index` (active id + order), `mpd:prop:<id>` (the property),
`mpd:ui:<id>` (per-property slider state), `mpd:locale` (UI language). `bootstrap()` seeds the sample
on first run.

## 5. The calculation engine

All engine globals are set by `setEngineFrom(prop)`. Then it computes `baseRun = amortize(0)` and
`BAL2035` (the balance at the end of the fixed period) as a reference run.

- `amortize(sonder, events, proj)` - month-by-month annuity. Monthly rate `MR = rate/12`. Sondertilgung
  is applied at the start of each year from `startYear+1` to the fixed end, capped at the balance.
  Phase 2 (after the fixed period) is always a projection, deviating from a simple continuation of
  today's payment only when the projected rate, term, or a manual payment differ.
- `refiPayment(rate)` - payment for the post-fixed period over the remaining term on the handover balance.
- `taxModel(rate)` - rental income vs deductions; the loss times the marginal rate is the yearly saving.
- `computeSonder(sonder)` - diffs an overpay run against `baseRun` (interest saved, months saved, etc.).
- `projectYears(g)` - per-year monthly projection to the fixed end; rent and costs grow at `g`.
- `saleScenario(g)` - value at `saleYears`, minus selling costs and remaining loan, minus net cash invested.
- `renoLeft(spent)` - remaining headroom under the 15% renovation limit.

**Precision rule:** the engine runs in full floating point with no intermediate rounding. The 2-decimal
rule is display only; never round inside the engine.

## 6. Multi-property

- **Switcher** - pills per property; clicking activates and re-renders.
- **Setup wizard** - 7 steps creating a `blankProperty()` (a clean neutral object; it does NOT clone the
  sample, to avoid leaking sample-specific values into new properties).
- **Manage panel ("Edit values")** - edits every calculation-affecting field. Scalars bind by a
  `data-path` attribute; dated cost/rent series have their own editors. This is the place to record a
  remortgage: change the current rate and payment, or set the follow-on terms.
- **Export/import** - one property to/from JSON; import creates a copy.
- **Jurisdiction gating** - `[data-de]` blocks show only for `country==='DE'`, so German tax commentary
  does not appear for non-DE properties.

## 7. Charts and interactivity

Canvas charts, `devicePixelRatio`-aware. Hover/tap tooltips use a hit-region system so every chart
reveals exact values, and a screen-reader table mirrors each chart. Charts: principal vs interest
split, balance over time, overpay comparison, rate scenarios, 10-year cashflow.

## 8. Localisation (DE / EN)

The app is about German housing finance, so the **number format stays `de-DE` in both languages**;
only the words change.

- **English is the default and is captured from the live DOM at startup** (`captureEn`), so it stays
  byte-identical and the test suite is stable. Only the German strings (`I18N_DE`) are authored by hand.
- **Static markup** carries `data-i18n` / `data-i18n-html` / `data-i18n-title` / `data-i18n-aria` keys
  that `applyI18n()` swaps. Nodes that mix static text with a dynamic child span keep that span inside
  the translated HTML so the render functions can refill it.
- **Dynamic strings** (sentences with live numbers, the wizard, the manage panel, chart tooltips,
  screen-reader tables, alerts) go through locale-aware builders in `TPL[LOCALE]`, accessed via `TL()`.
  These are independent strings per language, not word swaps, because German sentence structure differs.
- The German uses proper finance/tax register (Sondertilgung, Anschlussfinanzierung, Werbungskosten,
  Eigenaufwand, Restschuld, AfA, Sollzins / Effektivzins), not literal translation.
- A toggle in the property bar flips `LOCALE`, persists it to `localStorage`, re-applies the static
  dictionary, and re-renders everything (including charts). The maths is untouched by language.

## 9. Code principles

- Vanilla ES5-ish, one IIFE, no globals leaked, no dependencies.
- Formatting helpers are the single source of truth for display: `eur` (rounded), `eur2` (2 decimals),
  `deDec` (1 decimal, durations), `deDec2` (2 decimals, percentages), `deNum` (thousands-grouped integer).
- All displayed elements are addressed by id via `$('id')`; render functions set `textContent` /
  `innerHTML`. Keep id wiring intact (a test checks it).
- Defensive defaults: `blankProperty()` is neutral; `varRatePct` falls back to `fixedRate + 1.5` when zero.

## 10. Testing

Four layers (see `tests/README.md` for how to run them):

1. **In-app self-tests** - open with `?test`. Engine unit checks plus closed-form balance cross-checks
   at several rates, a negative-amortisation guard, and the Effektivzins-is-derived check. The sample's
   numeric baselines are this engine's own output (regression pins); the real correctness proofs are the
   closed-form cross-check and the independent Python harness.
2. **End to end (Playwright)** - `tests/e2e_test.py`: self-tests, sample renders, wizard add, switch
   isolation, dated edits, one-off Sondertilgung, follow-on rate projection, the edit-panel audit and a
   remortgage edit, export/import round-trip, delete, plus formatting assertions.
3. **Maths-accuracy harness** - `tests/analyst_check.py`: an independent Python amortiser plus pure
   closed-form annuity formulae, compared to the app engine (exposed as `window.MD_ENGINE` under
   `?test`) across a rate matrix with overpay, one-offs and manual payments. Agreement to the cent.
4. **Localisation** - `tests/i18n_test.py`: the DE/EN toggle, persistence, restore, wizard, manage panel,
   and that the `data-*` hooks survive translation, with no console errors.

## 11. Key design decisions (log)

- **Sollzins vs Effektivzins.** The nominal rate is the only rate input and drives the engine. The
  effective rate is an OUTPUT, derived by `effAnnual()` = `(1+r/12)^12 - 1`, shown labelled "derived".
- **Two-phase rate projection.** Phase 2 (after the fixed period) is always a clearly-labelled
  projection. It defaults to "same rate, same term" so the baseline equals a simple continuation of
  today's payment. Germany runs mortgages in two rate periods, which this models directly.
- **One-off Sondertilgung events** applied at the exact month, on top of the recurring annual amount.
  The baseline run carries no events so the "without overpaying" comparison stays honest.
- **Financing setup cost is first-rental-year only** and is kept out of the recurring deduction total,
  shown instead as a marked first-year line.
- **Negative-amortisation guard:** if a payment is below the monthly interest, the engine clamps
  principal at >= 0 so the balance cannot explode, and the UI warns.
- **`blankProperty()` is a clean object,** not a clone of the sample, so new properties never inherit
  sample-specific values.
