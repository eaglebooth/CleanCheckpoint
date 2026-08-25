# Runtime evidence

After manual deployment, record the exact Git commit and deployed-source SHA-256, then add an E2E matrix containing transaction hash, finality, execution result, contract return, authoritative state readback, and balance movement for:

- deterministic mutual-completion payout;
- disputed full payout;
- partial payout;
- provider no-show refund;
- evidence conflict and bounded recovery;
- wrong-role, wrong-value, stale-revision, and duplicate-settlement rejection.

Do not add expected or pending results as successful evidence.

## Current deployed-contract evidence

- [Studionet timeout matrix and happy payout](./STUDIONET_TIMEOUT_MATRIX.md) records the deployed-source parity, four deadline terminal exits, exact transfers, rejected duplicate recovery, and custody conservation for contract `0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016`.
- `STUDIONET_HAPPY_PATH.md` and `STUDIONET_DISPUTE_PATH.md` are retained as historical evidence for the previous deployment.
