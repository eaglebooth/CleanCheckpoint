# Changelog

## 2026-09-09 — Evidence Integrity & Prompt Security v2

- Replaced rendered-text trust with byte-exact SHA-256 verification for all three adjudication sources.
- Added single-use checkpoint digest indexing that rejects evidence replay before state mutation.
- Added full hexadecimal and zero-address validation for provider identities.
- Added explicit untrusted-source boundaries, a fixed output canary, and fail-closed integrity state.
- Exposed `integrity_status` through `get_job` and the contract workspace.
- Added four contract security regressions covering address spoofing, evidence replay, byte tampering, and prompt-canary manipulation.
- Deployed the Security v2 contract on Studionet at `0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c` and verified its empty-state interface.
- Completed the live Security v2 matrix: happy payout, verified semantic dispute, replay rollback, tamper fail-closed recovery, exact refunds, and zero residual custody.

## 2026-09-09

- Added a seven-stage, role-aware lifecycle guide to the live contract workspace.
- Added automatic client, provider, observer, and disconnected wallet classification.
- Added state-derived complete, available, and locked guidance for every lifecycle stage.
- Added four frontend unit tests covering role normalization and lifecycle progression.
- Preserved the current studionet contract and deployment address; this milestone requires no contract redeployment.

## 2026-08-29

- Added a public, wallet-free snapshot of the five settled studionet demonstrations.
- Added automatic studionet switch/add behavior before wallet writes.
- Preserved exact on-chain monetary values as strings in the frontend.
- Made newly created jobs load automatically and disabled duplicate actions while a transaction is pending.
- Added Explorer funding/network guidance, transaction verification links, and a compliant square logo.
- Documented the current contract, website, verification commands, and remaining Explorer seed requirement.
