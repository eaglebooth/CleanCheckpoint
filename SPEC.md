# CleanCheckpoint Specification

## Invariants

1. Only the stored provider may accept and bond a job.
2. Only the stored client may fund, schedule, or confirm completion.
3. Client funding must equal the locked fee exactly.
4. Every checkpoint is append-only and role-bound; a later revision must strictly increase.
5. Both roles must provide evidence before a dispute can open.
6. AI facts never contain a payout amount or recipient.
7. Paying and non-paying outcomes can never be consensus-equivalent.
8. Settlement and recovery are terminal and idempotent.
9. `total_held` decreases by exactly fee plus bond at terminal settlement.
10. A conflict or unverified fact cannot authorize a payout verdict.

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

## Evidence authority

The contract accepts only immutable gateway forms and stores exact URLs, SHA-256 declarations, actor wallet, source role, checkpoint kind, revision, and predecessor. Production deployments should additionally pin approved gateway hosts and booking-provider signatures. URL allowlisting alone is not claimed as proof of event truth.

## Resource bounds

- Titles: 4–100 characters.
- Evidence URLs: at most 500 characters.
- Jury input: at most 5,000 rendered characters per source.
- Jury output: four closed enums only.
- Public write methods never scan historical job or checkpoint counts.
