# Runtime evidence

After manual deployment, record the exact Git commit and deployed-source SHA-256, then add an E2E matrix containing transaction hash, finality, execution result, contract return, authoritative state readback, and balance movement for:

- deterministic mutual-completion payout;
- disputed full payout;
- partial payout;
- provider no-show refund;
- evidence conflict and bounded recovery;
- wrong-role, wrong-value, stale-revision, and duplicate-settlement rejection.

Do not add expected or pending results as successful evidence.
