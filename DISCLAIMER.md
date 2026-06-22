# Disclaimer

**This project is a software tool. It is not financial, tax, investment, or legal advice.**

The author is **not** a financial adviser, tax adviser, mortgage broker, or Steuerberater, and nothing
in this repository or the application constitutes professional advice or a recommendation to take (or
not take) any financial action.

## No reliance, no warranty, no liability

- Every number the tool produces, including balances, interest, amortisation schedules, tax
  estimates, overpayment effects, follow-on (Anschlussfinanzierung) projections, and sale forecasts,
  is **illustrative** and may be inaccurate or wrong.
- Projections and forecasts depend on assumptions you choose (interest rates, inflation, appreciation,
  deductions). The future is unknown; **do not treat any forecast as a guarantee.**
- Tax and legal rules change, vary by individual circumstances, and are applied here in a simplified
  way. Legal references (for example sections of the German EStG, or court rulings) are provided for
  general orientation only and may be out of date or inapplicable to your situation.
- The software is provided **"as is", without warranty of any kind**, express or implied. See the
  [Apache License 2.0](LICENSE), sections 7 (Disclaimer of Warranty) and 8 (Limitation of Liability).
- To the maximum extent permitted by law, the author **accepts no responsibility or liability** for
  any errors or omissions, or for any loss or damage arising from the use of, or reliance on, this
  tool or its output.

## Always seek professional advice

Before making any decision about a mortgage, property purchase, overpayment, refinancing, or tax
filing, consult a suitably qualified professional (a financial adviser, tax adviser, or Steuerberater)
who can take your full personal circumstances into account.

## Data

The application runs entirely in your browser, makes no network calls, and stores data only in your
browser's `localStorage` on your own device. The property bundled with the app is a **fictional
sample** with invented figures, not anyone's real loan, bank, account, address, or personal data.

## Validation, and comparison with other tools

The maths is checked against independent references: a from-scratch month-by-month amortiser, the
textbook closed-form annuity formula, and open-source amortisers, all reproduced to the cent in the
test suite. This validates the **arithmetic**, not the suitability of any result for your situation.

Results may legitimately differ from those of other mortgage calculators because of differing
conventions (for example, whether overpayments are booked at the start or end of the year, day-count
conventions, rounding, or how the effective rate folds in fees). A difference does not by itself mean
either tool is wrong. This project does **not** claim to match, replace, or be endorsed by, any other
named product or service.
