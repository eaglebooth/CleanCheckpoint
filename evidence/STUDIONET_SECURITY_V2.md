# Studionet Security v2 runtime evidence

- Date: 2026-09-09
- Network: GenLayer Studionet
- Contract: `0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c`
- Explorer: https://explorer-studio.genlayer.com/address/0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c
- Deployed source SHA-256: `e443300ec299b41494672a31ddef1b21f171de91bfceae70312a171a8fbadac7`

## Runtime matrix

### Job 0 — deterministic happy payout

- Create: `0x29372d204a748ca3daede8a17cef6d8784d0eea44390df71dddad1993045c0b6`
- Schedule: `0x5233ee8f86270d2dfbe774352e672ae0fd6e686490256beff0e356c698d21b26`
- Accept: `0xb4e5f2b2d37fb77b2317be292710923a62799c74a17b0ad42ad36f28d8c06c5a`
- Fund: `0x28dd20787f9bdfe5e6b53c9b3933d0a3311c70b955f5526438150b5e28b55f15`
- Completion checkpoint: `0x09be02c30e1cf7d2300cda01cf117cc25dc33fad112dfadd6141f973fac70327`
- Confirm and settle: `0x533daf3253ab147d0ad62ae740d3f0aec5abcbbd3ed0227d5430680d009b507c`
- Readback: `SETTLED`, `FULL_PAYOUT`; provider received 0.010 GEN and recovered the 0.001 GEN bond.

### Job 1 — semantic consensus dispute

- Create: `0xfc6c2ed0949c77063024ce115c976824601aa9b6726f3b17ca0bb1a11a7a3e5d`
- Provider checkpoint: `0x1f41a6d6b5d1f528572cc12d4fe0d5b3536b2987a552ce86c92e2254b6de4780`
- Client checkpoint: `0xb39e910e5e32f8c5a7fe63d1748fd89b392384c01709b25d3b6591b792b5bd35`
- Open dispute: `0x4cc6657adaf00376e04868d841290d4b663a4499a8c8ee3ca1cdf332955d33c9`
- Adjudicate: `0xba92e7679b483b571ebef54e0cc2da05427465437dfff0b7f611a3445026f8b5`
- Settle: `0x6b21b646575a805a9b9e5548f51b6aca1dd09e77f5b76b5f92274fac946ea169`
- Readback: `SETTLED`, `integrity_status=VERIFIED`, `PARTIAL_PAYOUT_75`; 0.0075 GEN paid to provider, 0.0025 GEN refunded to client, and 0.001 GEN bond returned.

### Job 2 — deadline recovery control

- Replay attempts: `0x30bff8c10d216cfea5c1bbc84344f37acacb81cc98a1900e1599133fa8910b7f`, `0x14618425d2f446c7f40bae13a606a67e6f958512cc8e2a0709b2fbbedd9adc26`
- Both finalized with validator agreement on an execution rollback whose payload was `EVIDENCE_ALREADY_USED`.
- Checkpoint count remained 3 after both attempts, proving no replay state mutation.
- Deadline recovery: `0xfbc8d2b58769d5822f3994dbf087c116abedbb8bef66ec70f3c1cb6a3782f2e7`.

### Job 3 — tampered evidence fails closed

- Create: `0xab92bc64d69f56fb82471695ecbb46f58ec1e18f30e830d46f036a565471d8cd`
- Tampered provider checkpoint: `0x444749a8f370f2350c97c2837fd4711935f9eff76cf24ed0e0698fa1c8bb6bce`
- Client checkpoint: `0x9a83900cf834defa63db8c3c4e547c621aff935e96a14b1b74d6c9f776170656`
- Open dispute: `0x99e1c520e78361af2ec3eff5b9c2c0aba10713e23fa676e375ff8f49b5183f9b`
- Adjudicate: `0x19ea42e1f56f3cc6ae47a618c2a57cad4d6913ad009ac23f1d5b3367063c6c52`
- Fail-closed readback: `integrity_status=FAILED`, `EVIDENCE_CONFLICT`, `RECOVERY`; the full 0.011 GEN remained held.
- Recover: `0xd2c6da23749611d644dfc288885477a65c7da364374ca2d4ae051ffe70d7b17e`
- Terminal readback: `SETTLED`, `EVIDENCE_RECOVERY`; client refunded 0.010 GEN and provider refunded 0.001 GEN.

## Final conservation readback

- Jobs: 4; checkpoints: 5
- Deposited: 0.044 GEN
- Held: 0 GEN
- Paid: 0.0185 GEN
- Refunded: 0.0255 GEN
- Contract balance: 0 GEN
- Invariant: `0.044 = 0 + 0.0185 + 0.0255` GEN.

