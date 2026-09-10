# Security v2 deployment gate

The source now changes storage and adjudication semantics, so it cannot replace the existing contract in place.

## Deployment

- Network: GenLayer Studionet
- Address: `0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c`
- Explorer: https://explorer-studio.genlayer.com/address/0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c
- Initial read verification: `get_totals` returned all six counters as zero.

## Runtime gate: complete

- Deterministic funded lifecycle: `FULL_PAYOUT` and terminal settlement.
- Semantic dispute: `integrity_status=VERIFIED` and `PARTIAL_PAYOUT_75`.
- Replayed digest: finalized `EVIDENCE_ALREADY_USED` rollback with no state mutation.
- Tampered digest: `integrity_status=FAILED`, `EVIDENCE_CONFLICT`, then bounded recovery.
- Final conservation: 0.044 GEN deposited = 0 held + 0.0185 paid + 0.0255 refunded; contract balance is zero.

Exact transactions and readbacks are recorded in `evidence/STUDIONET_SECURITY_V2.md`.

The previous v1 deployment remains documented in historical evidence at `0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016`.
