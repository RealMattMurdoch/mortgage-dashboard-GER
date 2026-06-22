# Contributing

Hi, I am Matt. Thanks for your interest. This is a small, single-file project, so the workflow is light.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Workflow (pull requests are the default)

Anyone can contribute, but changes land only through a reviewed pull request. There are **no direct
pushes to `main`**: every change is reviewed and approved by the owner
([@RealMattMurdoch](https://github.com/RealMattMurdoch)) before it is merged.

1. **Fork** the repo and create a branch from `main` (e.g. `fix/rounding`, `feat/extra-costs`).
2. Make your change in `Mortgage_Dashboard.html` (and the tests/docs if relevant).
3. Keep your own data out of it: real figures and notes live in the git-ignored
   [`private/`](private/) folder, never in the diff.
4. Run the test suite locally and confirm it is green (see below).
5. Open a pull request describing what changed and why. The PR template has a short checklist.
6. CI runs the full suite on your PR. The owner reviews, may request changes, and approves and merges.

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

---

## For the maintainer: enforcing review (one-time GitHub setup)

`.github/CODEOWNERS` already assigns every path to the owner, and `.github/workflows/ci.yml` runs the
tests on each pull request. To make owner approval and green tests **mandatory**, enable branch
protection once in the GitHub UI:

1. **Settings -> Branches -> Add branch ruleset** (or "Add classic branch protection rule") for `main`.
2. Turn on:
   - **Require a pull request before merging** (this blocks direct pushes to `main`).
   - **Require approvals** (set to 1).
   - **Require review from Code Owners** (this routes every PR to you via `CODEOWNERS`).
   - **Require status checks to pass before merging**, and select the `tests` workflow.
   - Optionally **Do not allow bypassing the above settings** (applies the rules to admins too).
3. Save. From then on, contributors fork and open PRs, CI must pass, and nothing merges into `main`
   without your approval.

If you want to also restrict who can open PRs at all, keep the repo public for forks (recommended for
an open project) rather than adding collaborators; forked PRs still require your approval to merge.

**Solo-owner note.** GitHub does not let you approve your own pull request. If you are the only
maintainer and require 1 approval, you would be unable to merge your own work. Fix this by adding
yourself to the ruleset's **bypass list** (Rulesets let you do this per actor): external contributors
still go fork -> PR -> your approval, while you can merge your own changes directly. Re-evaluate once
you have a second trusted reviewer.

**Recommended general settings** (Settings -> General -> Pull Requests):

- Enable **Allow squash merging** and disable merge commits, for a clean linear history.
- Enable **Automatically delete head branches** after merge.
- Enable **Require conversation resolution before merging** (also available in the ruleset).
- Under Settings -> Actions -> General, keep **Require approval for first-time contributors** so CI
  does not run automatically on a stranger's first PR until you allow it.
