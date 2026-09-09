# Security v2 deployment gate

The source now changes storage and adjudication semantics, so it cannot replace the existing contract in place.

## Deployment

- Network: GenLayer Studionet
- Address: `0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c`
- Explorer: https://explorer-studio.genlayer.com/address/0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c
- Initial read verification: `get_totals` returned all six counters as zero.

## Remaining runtime evidence

1. Run the deterministic funded lifecycle and semantic dispute against the new address.
2. Run a tampered-digest dispute and confirm `integrity_status=FAILED`, `status=RECOVERY`.
3. Confirm `deposited = held + paid + refunded` and `held = 0` after terminal settlement.

The previous v1 deployment remains documented in historical evidence at `0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016`.
