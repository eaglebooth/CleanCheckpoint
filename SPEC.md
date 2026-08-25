# CleanCheckpoint Specification

## Invariants

1. Only the stored provider may accept and bond a job.
2. Only the stored client may fund, schedule, or confirm completion.
3. Client funding must equal the locked fee exactly.
4. Every checkpoint is append-only and role-bound; a later revision must strictly increase.
5. A dispute requires a provider `COMPLETION` checkpoint and a client response checkpoint; arrival or work-start evidence is not completion.
6. AI facts never contain a payout amount or recipient.
7. Paying and non-paying outcomes can never be consensus-equivalent.
8. Settlement and recovery are terminal and idempotent.
9. `total_held` decreases by exactly the value reserved by that job at terminal settlement.
10. A conflict or unverified fact cannot authorize a payout verdict.
11. Every funded nonterminal state has a deadline-based terminal exit.
12. `total_deposited = total_held + total_paid + total_refunded` after every terminal path.
13. Provider earnings, provider bond refunds, client compensation, and client fee refunds are stored separately.

## Timeout settlement matrix

| State holding GEN | Due after | Evidence condition | Provider earned | Provider bond returned | Client compensation | Client fee refunded | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `PROVIDER_ACCEPTED` | service deadline | client did not fund | 0 | bond | 0 | 0 | `CLIENT_NON_FUNDING` |
| `CHECKPOINTS_ACTIVE` | recovery deadline | no provider completion | 0 | 0 | bond | fee | `PROVIDER_COMPLETION_DEFAULT` |
| `CHECKPOINTS_ACTIVE` | recovery deadline | completion exists, no client response | fee | bond | 0 | 0 | `CLIENT_RESPONSE_DEFAULT` |
| `CHECKPOINTS_ACTIVE` | recovery deadline | both roles submitted, no terminal action | 0 | bond | 0 | fee | `EVIDENCE_RECOVERY` |
| `DISPUTED` | recovery deadline | adjudication stalled/failed | 0 | bond | 0 | fee | `ADJUDICATION_TIMEOUT` |
| `RECOVERY` | recovery deadline | conflict/unavailable evidence | 0 | bond | 0 | fee | `EVIDENCE_RECOVERY` |
| `ADJUDICATED` | immediate | locked bounded verdict | deterministic share | bond | 0 | remaining fee | locked verdict |

Only the stored client or provider may invoke recovery. Early, outsider, and repeated calls fail before mutation. The state becomes `SETTLED` before any transfer is emitted.

## Decision matrix

| Precedence | Bounded facts | Derived result |
| --- | --- | --- |
| 1 | conflict = YES or any fact UNVERIFIED | EVIDENCE_CONFLICT |
| 2 | arrival = NO or completion = NONE | CLIENT_REFUND |
| 3 | completion = FULL and client_response = ACCEPTED | FULL_PAYOUT |
| 4 | completion = FULL | PARTIAL_PAYOUT_75 |
| 5 | completion = PARTIAL | PARTIAL_PAYOUT_50 |

## Consensus binding matrix

| Field | Origin | Persisted | Downstream effect | Binding |
| --- | --- | --- | --- | --- |
| arrival | semantic classifier | yes | refund eligibility | exact enum |
| completion | semantic classifier | yes | payout band | exact enum |
| client_response | semantic classifier | yes | full-payout eligibility | exact enum |
| conflict | semantic classifier | yes | recovery routing | exact enum |
| verdict | deterministic derivation | yes | settlement | derived only |
| payout amount | deterministic arithmetic | yes | transfer | never supplied by AI |

## Contract-level timeout tests

Direct Mode tests execute the actual contract class and assert authoritative readback for:

- client non-funding after provider bond;
- missing provider completion and bond compensation to the client;
- missing client response after provider completion;
- stalled adjudication;
- conflicting-evidence recovery;
- an already adjudicated verdict routed to deterministic settlement;
- early, outsider, and duplicate recovery rejection;
- arrival evidence not being accepted as completion;
- deadline entry points failing closed;
- value conservation and zero held balance at terminal state.

## Evidence authority

The contract accepts only immutable gateway forms and stores exact URLs, SHA-256 declarations, actor wallet, source role, checkpoint kind, revision, and predecessor. Production deployments should additionally pin approved gateway hosts and booking-provider signatures. URL allowlisting alone is not claimed as proof of event truth.

## Resource bounds

- Titles: 4–100 characters.
- Evidence URLs: at most 500 characters.
- Jury input: at most 5,000 rendered characters per source.
- Jury output: four closed enums only.
- Public write methods never scan historical job or checkpoint counts.
