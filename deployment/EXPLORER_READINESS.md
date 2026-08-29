# Project Explorer readiness

## Confirmed identity

- Project: CleanCheckpoint
- Status: Preview
- Primary category: Dispute Resolution
- Category tag 1: Evidence Assessment (`adjudicate` reads terms and both role-bound evidence sources)
- Category tag 2: Escrow Claims (`accept_job`, `fund_job`, `settle`, and `recover` custody and distribute GEN)
- Website: https://clean-checkpoint.vercel.app/
- GitHub: https://github.com/eaglebooth/CleanCheckpoint
- Contract: https://explorer-studio.genlayer.com/address/0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016
- Network: studionet
- Logo: `public/clean-checkpoint-logo.png` (1254 x 1254 PNG, under 2 MB)

## Current public state

The current contract exposes five settled jobs: client non-funding, missing provider completion, client-response timeout, adjudication timeout, and deterministic full payout. Contract schema and all public methods are readable from studionet.

## Blocker before submission

Seed one successful semantic dispute on the current contract: create job, set schedule, provider accepts and bonds 0.001 GEN, client funds 0.01 GEN, provider records COMPLETION, client records CLIENT_RESPONSE, open dispute, adjudicate, and settle. Verify a final `SETTLED` state with `PARTIAL_PAYOUT_75` or `PARTIAL_PAYOUT_50` on the current address.

Do not deploy a new contract for the frontend improvements in this release. Redeploy only if the current contract source must change or the Studio address stops returning its schema.
