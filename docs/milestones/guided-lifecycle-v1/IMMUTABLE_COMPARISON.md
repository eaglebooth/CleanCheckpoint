# Guided Lifecycle UX — Immutable Milestone Comparison

## Reviewer summary

This document identifies exactly which work belongs to the **Guided Lifecycle UX — Role-Aware Contract Workspace** milestone. The comparison uses full commit hashes so the reviewed range cannot move when the repository receives later upgrades.

## Immutable comparison

| Boundary | Commit | Meaning |
|---|---|---|
| Final reviewed project version | [`6aa70f019b64c4b74f74fb873049c4ae380a65ec`](https://github.com/eaglebooth/CleanCheckpoint/commit/6aa70f019b64c4b74f74fb873049c4ae380a65ec) | CleanCheckpoint immediately before this milestone |
| Milestone version with requested evidence correction | [`ef0437f92be6585912f0926d5943f45aad00aaff`](https://github.com/eaglebooth/CleanCheckpoint/commit/ef0437f92be6585912f0926d5943f45aad00aaff) | Guided lifecycle implementation plus corrected before/after evidence |

**Review the exact milestone diff:**

<https://github.com/eaglebooth/CleanCheckpoint/compare/6aa70f019b64c4b74f74fb873049c4ae380a65ec...ef0437f92be6585912f0926d5943f45aad00aaff>

The immutable range contains **13 changed files, 140 additions, and 6 deletions**.

## What changed in this milestone

### Before

The accepted project exposed eight contract actions as an undifferentiated button grid. A visitor had to infer:

- which wallet role was connected;
- which actions belonged to the client or provider;
- the correct order of contract calls;
- which stages were already complete;
- why later actions were unavailable.

![Workspace before the milestone](./before.png)

### After

The workspace provides a seven-stage guided lifecycle derived from authoritative `get_job` contract fields. It identifies four wallet contexts—client, provider, observer, and disconnected—and gives every stage one of three explicit states:

- `complete`: confirmed by contract state;
- `available`: callable by the connected role now;
- `locked`: unavailable, with a reason explaining the missing role or prerequisite.

![Workspace after the milestone](./after.png)

## Files and responsibilities

| File | Milestone contribution |
|---|---|
| `src/lib/lifecycle.ts` | Pure role detection, stage derivation, and progress calculation from contract state |
| `src/components/AppShell.tsx` | Integrates the guided lifecycle into the live contract workspace |
| `src/app/lifecycle.css` | Visual hierarchy for complete, available, and locked stages |
| `tests/lifecycle.test.ts` | Four unit tests covering address normalization and lifecycle progression |
| `docs/milestones/guided-lifecycle-v1/` | Immutable before/after screenshots and milestone explanation |
| `README.md` and `CHANGELOG.md` | Public feature and release documentation |

Minor configuration changes in the comparison enable the new UI tests and keep lint/build verification reproducible.

## Why this work is new

The base commit does not contain `src/lib/lifecycle.ts`, `src/app/lifecycle.css`, or `tests/lifecycle.test.ts`. Those files and their AppShell integration first appear inside the immutable comparison range. Later security and contract upgrades are intentionally excluded so this milestone can be evaluated independently without claiming previously reviewed work.

## Verification path

From the milestone commit, a reviewer can run:

```bash
npm install
npm run test:ui
python -m pytest tests -p no:cacheprovider
npm run lint
npm run build
```

The lifecycle progression tests verify that UI guidance is computed from live contract fields rather than optimistic browser-only state. This milestone changes UX and tests only; it does not change contract custody semantics or require a new deployment.

## Evidence links

- [Immutable GitHub comparison](https://github.com/eaglebooth/CleanCheckpoint/compare/6aa70f019b64c4b74f74fb873049c4ae380a65ec...ef0437f92be6585912f0926d5943f45aad00aaff)
- [Milestone implementation commit](https://github.com/eaglebooth/CleanCheckpoint/commit/9f8afee3a0910fcac9a78c4cb9fe7dde267a32c8)
- [Requested screenshot correction](https://github.com/eaglebooth/CleanCheckpoint/commit/ef0437f92be6585912f0926d5943f45aad00aaff)
- [Original milestone overview](./README.md)
- [Live application](https://clean-checkpoint.vercel.app/)
