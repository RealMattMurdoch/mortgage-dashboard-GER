# `private/` - your own data lives here (never committed)

This folder is **git-ignored** (everything except this README). It is where you, or any other person
using the tool, keep real data separate from the public code, while still being able to pull updates
and contribute changes back.

## What to put here

- **Property exports** from the app's `Export` button (`*.json`).
- **Personal notes** about your mortgage, tax situation, or scenarios.
- **Local experiments** or a personal copy of the app you have tweaked for yourself.

Anything in this folder (other than this README) is ignored by git, so it can never be pushed to the
public repository by accident.

## Why this separation exists

The repository ships only a **fictional sample property**. The actual app keeps your data in your
browser (`localStorage`), and you can export it to JSON. Keeping those exports and any personal notes
under `private/` means:

- You can `git pull` new versions of the app without your data ever being tracked.
- You can fork the repo, make code improvements, and open a pull request that contains **only code**,
  with no risk of leaking your figures.
- The same workflow works for everyone: maintainer and contributors alike.

## The bigger picture (two tiers)

1. **Public repo** (this repository): the app, a fictional sample, docs, and tests. This is what gets
   cloned and what pull requests target.
2. **Your private data and personal build**: this `private/` folder for data, and optionally a separate
   private repository for any deep personal customisation. Keep real loan, bank, account, and address
   details out of the public repo entirely.

> If you customise the app heavily for your own use, consider keeping that personal version in a
> separate **private** Git repository, and only contribute generic, reusable improvements back here.
