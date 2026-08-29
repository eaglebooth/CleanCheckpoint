# CleanCheckpoint

CleanCheckpoint is a GenLayer-native cleaning-service protocol built around append-only, role-bound service checkpoints. Clients lock service terms and fees; providers bond accepted work; both parties attest to lifecycle events. Mutual completion settles deterministically. Only a disputed job invokes semantic consensus.

## Architecture difference statement

This is not a renamed single-review escrow. Its primitive is an append-only checkpoint ledger: evidence accumulates per actor and revision throughout a job, the common path bypasses AI, and the exception path asks validators for four bounded facts. The contract—not the model—derives the payout band from those facts. Corrections create predecessor-linked revisions instead of replacing an evidence packet, and a conflicting verdict enters a timed recovery state rather than allowing a second ad-hoc review.

## Why GenLayer

A normal contract can settle mutual agreement, but it cannot reliably interpret conflicting narrative records from a client and provider. GenLayer validators independently fetch the locked sources and agree on `arrival`, `completion`, `client_response`, and `conflict`. Those facts have direct custody consequences, while deterministic code retains control of amounts and recipients.

## Lifecycle

```text
JOB_OPEN -> PROVIDER_ACCEPTED -> CHECKPOINTS_ACTIVE
CHECKPOINTS_ACTIVE -> SETTLED                         (mutual completion)
CHECKPOINTS_ACTIVE -> DISPUTED -> ADJUDICATED -> SETTLED
DISPUTED -> RECOVERY -> SETTLED                      (unavailable/conflicting evidence)
PROVIDER_ACCEPTED -> SETTLED                          (client non-funding timeout)
CHECKPOINTS_ACTIVE -> SETTLED                         (completion/response timeout)
DISPUTED | RECOVERY -> SETTLED                       (stalled adjudication/evidence timeout)
```

## Current deployment

- Website: https://clean-checkpoint.vercel.app/
- Network: GenLayer studionet (`Preview` in Project Explorer)
- Contract: `0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016`
- Explorer: https://explorer-studio.genlayer.com/address/0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016
- Demonstration cost: client fee `0.01 GEN`; provider bond `0.001 GEN`.

The landing page reads the latest settled demonstrations without requiring a wallet. Writes require two funded wallets and automatically request the GenLayer Studio network.

## Verification

```bash
python -m pytest tests -p no:cacheprovider
npm run lint
npm run build
```

Runtime evidence for the current deployment lives in `evidence/STUDIONET_TIMEOUT_MATRIX.md`. Explorer submission readiness and the remaining semantic-dispute seeding step live in `deployment/EXPLORER_READINESS.md`.

## Local setup

```bash
npm install
copy .env.example .env.local
npm run dev
```

Configure a deployed address from the header menu. The app uses `genlayer-js`, requests the wallet provider only for writes, waits for acceptance, inspects execution metadata when available, and re-reads the affected job before showing verified success.

## Contract interface

- `create_job(...)`: locks the client, provider, service, fee, terms URL and digest.
- `set_schedule(...)`: locks strict service/challenge/recovery ordering.
- `accept_job(job_id)`: provider-only payable bond.
- `fund_job(job_id)`: client-only exact-fee custody.
- `record_checkpoint(...)`: appends a role-authorized immutable evidence revision.
- `confirm_completion(job_id)`: deterministic happy-path payout.
- `open_dispute(job_id)`: requires evidence from both roles.
- `adjudicate(job_id)`: semantic classification of four bounded facts.
- `settle(job_id)`: deterministic payout calculation and transfers.
- `recover(job_id)`: permissionless-for-parties terminal router covering every funded nonterminal state.
- `get_job(job_id)`, `get_totals()`: reviewer-facing authoritative views.

## Trust boundaries and limitations

- The MVP does not judge photos, cleanliness aesthetics, identity, location, or private-home imagery.
- An immutable IPFS/Arweave URL proves content immutability, not the real-world truth of an event. Source roles and case linkage limit substitution but do not replace a trusted booking/check-in attestor.
- For production, add provider-signed booking/check-in attestations and a vetted evidence gateway registry.
- GenLayer is unnecessary when both parties agree; that path is intentionally deterministic.
- Semantic consensus can remain unresolved. The contract fails closed into bounded recovery instead of claiming a successful verdict.

## Deadline terminal exits

| Funded state | Deadline | Missing obligation | Terminal result |
| --- | --- | --- | --- |
| `PROVIDER_ACCEPTED` | service deadline | client never funds | `CLIENT_NON_FUNDING`: provider bond returned |
| `CHECKPOINTS_ACTIVE` | recovery deadline | provider has no completion checkpoint | `PROVIDER_COMPLETION_DEFAULT`: client fee refunded and provider bond paid to client |
| `CHECKPOINTS_ACTIVE` | recovery deadline | provider completed; client never responds | `CLIENT_RESPONSE_DEFAULT`: provider receives fee and bond return |
| `CHECKPOINTS_ACTIVE` | recovery deadline | both parties submitted but no terminal action | neutral evidence recovery: each principal returned |
| `DISPUTED` | recovery deadline | adjudication stalled or failed | `ADJUDICATION_TIMEOUT`: each principal returned |
| `RECOVERY` | recovery deadline | evidence remained conflicting/unavailable | `EVIDENCE_RECOVERY`: each principal returned |
| `ADJUDICATED` | callable immediately | settlement not yet called | locked verdict is settled; timeout cannot rewrite it |

All routes close state before transfer, reject outsiders and repeat calls, and preserve `deposited = held + paid + refunded`.

## Release policy

Deployment is intentionally not automated. Before submission, run the local suite and lint, deploy manually after approval, then add Explorer transactions and source-hash parity under `evidence/`.
