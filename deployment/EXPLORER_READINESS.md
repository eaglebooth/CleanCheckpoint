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

Security v2 is deployed with a clean state. The `get_totals` schema was read successfully from Studionet with zero jobs, checkpoints, deposits, and held funds. Historical v1 lifecycle evidence remains under `evidence/` and is intentionally labeled with its original address.

## Blocker before submission

Seed the Security v2 address with a deterministic funded lifecycle, a successful semantic dispute, and a tampered-digest recovery. Verify `integrity_status=VERIFIED` for the semantic result, `integrity_status=FAILED` for tampered evidence, and zero held funds after terminal settlement.

Do not redeploy again for frontend-only improvements. The next address change is justified only by a new contract milestone or a failed source-parity check.
