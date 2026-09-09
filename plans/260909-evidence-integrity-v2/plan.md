# Evidence Integrity & Prompt Security v2

## Goal

Turn evidence digests from stored declarations into enforced adjudication inputs, prevent checkpoint reuse, and harden untrusted-source handling. This is a contract-level security milestone, separate from the v1 guided-workspace UX milestone.

## Baseline

- Immutable URL and SHA-256 syntax are validated at write time.
- Adjudication renders source text but does not recompute committed digests.
- The same checkpoint digest can be attached to multiple jobs.
- Prompt states that evidence is untrusted, but has no explicit source boundary/canary regression coverage.

## Design

1. Fetch exact source bytes with `gl.nondet.web.get` during adjudication.
2. Recompute lowercase `sha256:` digests before any text reaches the LLM.
3. Fail closed to `EVIDENCE_CONFLICT` when a required source is unavailable, undecodable, too short, or mismatched.
4. Add a global checkpoint-digest index; reject duplicate evidence before mutation.
5. Validate all 40 address nibbles, then normalize to lowercase.
6. Frame each verified source inside explicit `UNTRUSTED_*` boundaries and require a fixed canary field in model output.
7. Surface integrity status in `get_job` and the frontend workspace.

## Files

- Modify `contracts/CleanCheckpoint.py`: hashing, reuse index, strict address validation, guarded jury input/output.
- Modify `tests/test_genlayer_direct.py`: digest, reuse, tamper, injection, address, and fail-closed tests.
- Modify `tests/test_contract_static.py`: security markers.
- Modify frontend types/state card to display integrity verdict.
- Add milestone evidence and update README, SPEC, CHANGELOG, deployment docs.

## Success criteria

- Tampered bytes never reach a paying verdict.
- Duplicate checkpoint digest is rejected without incrementing `checkpoint_count`.
- Prompt-injection text cannot omit/change the output canary without fail-closed recovery.
- Existing custody, timeout, and conservation tests remain green.
- New deployment uses a fresh Studionet address and frontend env is updated only after live verification.

## Deployment dependency

Contract storage and adjudication logic change. A new manual Studionet deployment is required after local verification; the current production address must remain active until the replacement lifecycle is proven.
