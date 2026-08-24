# Studionet Runtime Evidence

Test date: 2026-08-24

Contract: `0x6e2A785B1699067F8573e765B601f651917D7e47`

Explorer: https://explorer-studio.genlayer.com/address/0x6e2A785B1699067F8573e765B601f651917D7e47

## Source parity

- Local normalized source SHA-256: `d86267fa2a4f3cb611ae28a03bc0a1dd08cdb916ff5f5afa7a24bcf15b4eca96`
- Deployed normalized source SHA-256: `d86267fa2a4f3cb611ae28a03bc0a1dd08cdb916ff5f5afa7a24bcf15b4eca96`
- Exact normalized equality: `TRUE`
- Character count on both sides: `18767`

## Actors and value

- Client: `0x2da5393d7bbb9a037dc3abb56dbbc5c150fc843f`
- Provider: `0xeb57bc7125fa60d7482ce12058397369ab3581f8`
- Job ID: `0`
- Fee: `0.01 GEN`
- Provider bond: `0.001 GEN`
- Maximum custody observed: `0.011 GEN`

## Transaction matrix

| Step | Transaction | Final status | Consensus result | Authoritative readback |
| --- | --- | --- | --- | --- |
| Create job | `0x46259e39f0bfa2269424aed1b9356a2abe20edc995cd75f83f27972de1001acf` | FINALIZED | MAJORITY_AGREE | `jobs=1`, job `0` exists |
| Lock schedule | `0x95ae279afcf1b0157f570ce42676ee661e9ef02b77cac9d98b0ce928091bbdfe` | FINALIZED | MAJORITY_AGREE | Strict service/challenge/recovery timestamps persisted |
| Provider accept + bond | `0x83413bcc1d50895b74a295e7d8c04e8a26b7e9bc6a603210e6f43f77409f6c07` | FINALIZED | MAJORITY_AGREE | `status=PROVIDER_ACCEPTED`, `held=0.001 GEN` |
| Client fund | `0x50bcf0e28a8ad78d723436e5cf9259ded9ab486c9eeb6aee003a081e6735b008` | FINALIZED | MAJORITY_AGREE | `status=CHECKPOINTS_ACTIVE`, `held=0.011 GEN`, contract balance `0.011 GEN` |
| Provider checkpoint | `0x86e8e4c33d760cf8054a0771fbeebf5585ec0b24f1ccf5d68d24edf8ab79ffba` | FINALIZED | MAJORITY_AGREE | `checkpoints=1` |
| Client confirms completion | `0x1d41f30fdeb7d23309a2825af403403d9639ad33bb334a85e28e2e5c789f3b3d` | FINALIZED | MAJORITY_AGREE | `status=SETTLED`, `verdict=FULL_PAYOUT`, `provider_paid=0.011 GEN` |

## Custody and payout proof

Before funding:

- Contract balance: `0`
- Internal held ledger: `0`

At full custody:

- Contract balance: `0.011 GEN`
- Internal held ledger: `0.011 GEN`
- Job status: `CHECKPOINTS_ACTIVE`

After settlement and triggered EVM transfer:

- Contract balance: `0`
- Internal held ledger: `0`
- Internal paid ledger: `0.011 GEN`
- Provider balance increased by exactly `0.011 GEN`
- Job status: `SETTLED`
- Verdict: `FULL_PAYOUT`

## Verification boundary

This run proves the deterministic mutual-completion path, role-bound provider checkpoint, real custody, real payout, terminal state, and source parity. It does not claim the semantic dispute path passed: the old IPFS gateway resource was not independently retrievable during this run. A separate public cleaning-specific evidence packet and `DISPUTED -> ADJUDICATED/RECOVERY -> SETTLED` run are still required before submission.
