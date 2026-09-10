# Project Explorer readiness

## Confirmed identity

- Project: CleanCheckpoint
- Status: Preview
- Primary category: Dispute Resolution
- Category tag 1: Evidence Assessment (`adjudicate` reads terms and both role-bound evidence sources)
- Category tag 2: Escrow Claims (`accept_job`, `fund_job`, `settle`, and `recover` custody and distribute GEN)
- Website: https://clean-checkpoint.vercel.app/
- GitHub: https://github.com/eaglebooth/CleanCheckpoint
- Contract: https://explorer-studio.genlayer.com/address/0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c
- Network: studionet
- Logo: `public/clean-checkpoint-logo.png` (1254 x 1254 PNG, under 2 MB)

## Current public state

Security v2 is deployed and seeded with four reproducible runtime scenarios: happy settlement, verified semantic dispute, replay rejection, and tamper recovery. Final totals are 4 jobs, 5 checkpoints, 0.044 GEN deposited, 0 held, 0.0185 paid, and 0.0255 refunded. Historical v1 lifecycle evidence remains under `evidence/` and is intentionally labeled with its original address.

## Submission status

The Security v2 runtime gate is complete. Exact transaction hashes and authoritative readbacks are in `evidence/STUDIONET_SECURITY_V2.md`.

Do not redeploy again for frontend-only improvements. The next address change is justified only by a new contract milestone or a failed source-parity check.
