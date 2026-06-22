<!-- Thanks for contributing! Pull requests are the default way changes get in here.
     Every PR is reviewed by the owner (@RealMattMurdoch) before merge. -->

## What does this change?

<!-- A short description of the change and why. Link any related issue (e.g. "Closes #12"). -->

## Type

- [ ] Bug fix
- [ ] New feature / enhancement
- [ ] Docs only
- [ ] Refactor / cleanup

## Checklist

- [ ] I ran the test suite locally and it is green:
      `python tests/e2e_test.py`, `python tests/analyst_check.py`, `python tests/i18n_test.py`
- [ ] If I changed the maths, `analyst_check.py` still agrees to the cent.
- [ ] If I added or changed UI text, I updated **both** English (`data-i18n` / `TPL.en`) and German
      (`I18N_DE` / `TPL.de`), and `i18n_test.py` passes.
- [ ] No real personal data (loan, bank, account, address, email) anywhere in the diff or commits.
- [ ] No em dashes or en dashes; 2-decimal money/percentages; `de-DE` number format kept.
- [ ] The app is still a single dependency-free HTML file (no build step, no new runtime deps).

## Notes for the reviewer

<!-- Anything you want the owner to look at closely. For a maths change, include the inputs so it can
     be reproduced against analyst_check.py. -->
