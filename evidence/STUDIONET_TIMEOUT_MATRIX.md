# Studionet Timeout and Payout Evidence

Test date: 2026-08-25

Contract: `0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016`

Explorer: https://explorer-studio.genlayer.com/address/0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016

## Source parity

- Local normalized source SHA-256: `37e2a32214eea9a699ade440b4179fc97a523ee405a2a74039abd7806822b082`
- Deployed normalized source SHA-256: `37e2a32214eea9a699ade440b4179fc97a523ee405a2a74039abd7806822b082`
- Exact normalized equality: `TRUE`

## Public immutable inputs

- Terms: https://gateway.pinata.cloud/ipfs/QmQBQDCyfCNC63GBDCSP7WfTNBkTSWSRpUg4Hr7aZjAdKH
- Terms digest: `sha256:03d4c0e4185b0a7da060a9f1efc0e29cf6e6d3cc9ae3030de56de7c754873cff`
- Completion: https://gateway.pinata.cloud/ipfs/QmWzpoMsDRrAWfWaLoY21QmwsStcYY8Z66k8yvG8rGsfgP
- Completion digest: `sha256:c9dee431e40daf70e2ac0ebe94d3585356ee6677990f3a2687ae09cbfae20719`

## Deadline terminal exits

| Job | Funded state and missing action | Recovery transaction | Terminal verdict | Exact settlement |
| --- | --- | --- | --- | --- |
| 0 | `PROVIDER_ACCEPTED`; client never funds | `0x9c525e42fc5af7c860f7ebd26bc873f6f71f3e0688df32cb8352305e05f6e869` | `CLIENT_NON_FUNDING` | Provider bond refund `0.001 GEN`; client and provider earnings `0` |
| 1 | `CHECKPOINTS_ACTIVE`; provider never records completion | `0xb8c59883f3047e240fe2001c220b1fd1c0ea389d8c7a673eaebbc7b9ab6ce7af` | `PROVIDER_COMPLETION_DEFAULT` | Client fee refund `0.01 GEN` plus provider bond compensation `0.001 GEN` |
| 2 | Completion exists; client never responds | `0xfc98a165b89e0b13e19539d191ad71ffda335642dd674ddd61a56f49e28fef38` | `CLIENT_RESPONSE_DEFAULT` | Provider service payout `0.01 GEN` plus bond refund `0.001 GEN` |
| 3 | `DISPUTED`; adjudication stalls past recovery deadline | `0xd7d40b3803acb3939b640b0df9875fe1616cbf4635e372e07307a58b3ca14e41` | `ADJUDICATION_TIMEOUT` | Provider bond refund `0.001 GEN`; client fee refund `0.01 GEN` |

All four recovery transactions finalized with `MAJORITY_AGREE`. Job readback is `SETTLED` for every row.

## Happy-path organizer payout

Job `4` uses a long schedule and real IPFS terms/completion evidence.

| Step | Transaction |
| --- | --- |
| Create job | `0xb71a8a023ecb5026b2c7f48e3de4acc111d285646955f768154e977e48595b23` |
| Lock schedule | `0x68a7410ddb5a9f4559b33be8acb21a8c88865a184a59f6a35a21815af62f657a` |
| Provider locks `0.001 GEN` bond | `0x4b4c0da497b61f069a448761654a62c309b195885d6ad2827220c0cd06aa22c1` |
| Client locks `0.01 GEN` fee | `0x25feec8a20cd2dc86683d8544cef126c4bb1908987dfadd0aa29a52c4c61f1ab` |
| Provider records bound completion | `0x8193e7674e1ea10a500ad513d8cf2feb0a657f42ffa13ae71989e417d7f6d8b3` |
| Client confirms and settles | `0xc96c40272842d535804474aeb949c5acc3fe15c40edfc14343474eee842d6994` |

Authoritative readback: `status=SETTLED`, `verdict=FULL_PAYOUT`, `provider_paid=0.01 GEN`, and `provider_refunded=0.001 GEN`.

## Failure and conservation proof

- A repeated recovery finalized as a contract rollback with `NOT_RECOVERABLE`: `0xd3bb6230137c17561b8e5a2e82de6ec2e1ce76019d02c4254becb765dfadcf67`.
- Final totals: deposited `0.045 GEN`, held `0`, paid `0.021 GEN`, refunded `0.024 GEN`.
- Conservation: `0.045 = 0 + 0.021 + 0.024 GEN`.
- Transaction acceptance is not treated as business success: runtime callers inspect nested receipt payloads and surface rollback/contract-error results.
