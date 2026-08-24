# Studionet Semantic Dispute Evidence

Test date: 2026-08-24

Contract: `0x6e2A785B1699067F8573e765B601f651917D7e47`

Job ID: `1`

Explorer: https://explorer-studio.genlayer.com/address/0x6e2A785B1699067F8573e765B601f651917D7e47

## Public evidence verification

Three cleaning-specific JSON artifacts were uploaded separately to Pinata. Each URL was fetched back through the public Pinata gateway. The fetched byte length and SHA-256 matched the local source exactly.

| Role | CID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Terms | `QmQBQDCyfCNC63GBDCSP7WfTNBkTSWSRpUg4Hr7aZjAdKH` | 582 | `03d4c0e4185b0a7da060a9f1efc0e29cf6e6d3cc9ae3030de56de7c754873cff` |
| Provider completion | `QmWzpoMsDRrAWfWaLoY21QmwsStcYY8Z66k8yvG8rGsfgP` | 442 | `c9dee431e40daf70e2ac0ebe94d3585356ee6677990f3a2687ae09cbfae20719` |
| Client response | `QmeGVuNHeq9Vs21QSRFzNW3TxR19eXijfbropBteGdP1To` | 563 | `1eb2a75bdc6bce174d6f06df3f05117fad0ee35222d5106e32e9b664d60a0ba2` |

Full URLs and exact digests are recorded in `PINATA_MANIFEST.json`.

## Transaction matrix

| Step | Transaction | Status | Consensus | State proof |
| --- | --- | --- | --- | --- |
| Create job | `0xc47d3dc9a4ea0d0f49647494e857d0414e94aa26e172964297a229603761f04f` | FINALIZED | MAJORITY_AGREE | Job `1` created with Pinata terms |
| Lock schedule | `0x6d42fa419a41ec1d078a689be9da66e48a696832f11e2a62df005a82c137ff37` | FINALIZED | MAJORITY_AGREE | Ordered deadlines persisted |
| Accept and bond | `0x534b86b42c5e0c9d21339f860c47afc841434c7935cae3595663a05d845deab9` | FINALIZED | MAJORITY_AGREE | Provider role accepted with `0.001 GEN` bond |
| Fund | `0xcf6b94ca5e52d42b41e5db7e6bf6f58c4de5710fa74ec49d647c501a601db608` | FINALIZED | MAJORITY_AGREE | `CHECKPOINTS_ACTIVE`; contract held `0.011 GEN` |
| Provider evidence | `0xd412901f7e38e7ee26d3b62725c816a8911d82de7c81c039569e127ce227d7ac` | FINALIZED | MAJORITY_AGREE | Provider-role completion checkpoint appended |
| Client evidence | `0xadaa07c519f7b5e5c6724ae0a17427bc22ac22c653b35cd90dce1361e4dca164` | FINALIZED | MAJORITY_AGREE | Client-role response checkpoint appended |
| Open dispute | `0x5f87ae46884fd408098f97349f08adb9c9f8d19ea740cd08412e8a1d8a134043` | FINALIZED | MAJORITY_AGREE | Job entered `DISPUTED` |
| Semantic jury | `0x40f10295629737de5a51686b3488199d82a2a00fa83bc7102c20888ae8a810b2` | FINALIZED | MAJORITY_AGREE | Contract derived `PARTIAL_PAYOUT_75` and `ADJUDICATED` |
| Settle | `0x2b56db65fec55e280de806e2ee4077df4cf13da935230ca54bba30c6e35aa31b` | FINALIZED | MAJORITY_AGREE | Job entered `SETTLED`; custody returned to zero |

## Economic result

- Client fee: `0.01 GEN`
- Provider bond: `0.001 GEN`
- Maximum contract custody: `0.011 GEN`
- Jury facts implied the deterministic band: `PARTIAL_PAYOUT_75`
- Provider gross payout: `0.0085 GEN` (`0.0075 GEN` service share + `0.001 GEN` returned bond)
- Client refund: `0.0025 GEN`
- Provider net balance change across bond and settlement: `+0.0075 GEN`
- Client net balance change across funding and refund: `-0.0075 GEN`
- Final contract balance: `0`
- Final internal held ledger: `0`

This run proves public source retrieval by validators, semantic consensus over bounded facts, deterministic payout derivation, two-role evidence, real custody, split transfers, terminal state, and value conservation.
