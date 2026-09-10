"""Security v2 Studionet adversarial lifecycle: replay rejection and tamper recovery."""

import json
import os
import time

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


ADDRESS = os.environ.get("CLEANCHECKPOINT_CONTRACT_ADDRESS", "0xfc6c3abc5C202A37c8389a96b15165f2Fc5D7e1c")
RPC_URL = "https://studio.genlayer.com/api"
FEE, BOND = 10**16, 10**15
TERMS_URL = "https://gateway.pinata.cloud/ipfs/QmQBQDCyfCNC63GBDCSP7WfTNBkTSWSRpUg4Hr7aZjAdKH"
TERMS_DIGEST = "sha256:03d4c0e4185b0a7da060a9f1efc0e29cf6e6d3cc9ae3030de56de7c754873cff"
PROVIDER_URL = "https://gateway.pinata.cloud/ipfs/QmWzpoMsDRrAWfWaLoY21QmwsStcYY8Z66k8yvG8rGsfgP"
TAMPERED_DIGEST = "sha256:" + ("f" * 64)
REPLAYED_DIGEST = "sha256:c9dee431e40daf70e2ac0ebe94d3585356ee6677990f3a2687ae09cbfae20719"


def parse(value):
    return json.loads(value) if isinstance(value, str) else value


def main():
    client_signer = os.environ.get("CLEANCHECKPOINT_CLIENT_SIGNER", "")
    provider_signer = os.environ.get("CLEANCHECKPOINT_PROVIDER_SIGNER", "")
    if not client_signer or not provider_signer:
        raise RuntimeError("Set both ephemeral CleanCheckpoint test signer environment variables.")
    client_account, provider_account = create_account(client_signer), create_account(provider_signer)
    chain = create_client(chain=studionet, account=client_account, endpoint=RPC_URL)

    def read(name, args=None):
        return parse(chain.read_contract(address=ADDRESS, function_name=name, args=args or [], account=client_account))

    def submit(account, method, args, value=0):
        tx = str(chain.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value))
        print(json.dumps({"event":"TX_SUBMITTED","method":method,"tx":tx}, sort_keys=True), flush=True)
        return tx

    def wait(label, predicate, timeout=600):
        end, last = time.time() + timeout, ""
        while time.time() < end:
            state = predicate()
            encoded = json.dumps(state, sort_keys=True, default=str)
            if encoded != last:
                print(json.dumps({"event":label,"state":state}, sort_keys=True, default=str), flush=True)
                last = encoded
            if state.get("ready"):
                return state
            time.sleep(5)
        raise TimeoutError(label)

    initial = read("get_totals")
    resume_job_id = os.environ.get("CLEANCHECKPOINT_RESUME_JOB_ID")
    job_id = int(resume_job_id) if resume_job_id is not None else int(initial["jobs"])
    checkpoint_before = int(initial["checkpoints"])
    held_before = int(initial["held"])
    txs = {}
    if resume_job_id is None:
        txs["create_job"] = submit(client_account, "create_job", ["Security v2 tamper recovery", "HOME", provider_account.address, FEE, TERMS_URL, TERMS_DIGEST])
        wait("JOB_CREATED", lambda: {"ready":int(read("get_totals")["jobs"]) > job_id, "totals":read("get_totals")})
        now = int(time.time())
        txs["set_schedule"] = submit(client_account, "set_schedule", [job_id, now + 300, now + 420, now + 540])
        wait("SCHEDULE", lambda: {"ready":int(read("get_job", [job_id])["recovery_deadline"]) > now, "job":read("get_job", [job_id])})
        txs["accept_job"] = submit(provider_account, "accept_job", [job_id], BOND)
        wait("ACCEPTED", lambda: {"ready":read("get_job", [job_id])["status"] == "PROVIDER_ACCEPTED", "job":read("get_job", [job_id])})
        txs["fund_job"] = submit(client_account, "fund_job", [job_id], FEE)
        wait("FUNDED", lambda: {"ready":read("get_job", [job_id])["status"] == "CHECKPOINTS_ACTIVE", "job":read("get_job", [job_id]), "totals":read("get_totals")})
    else:
        job = read("get_job", [job_id])
        if job["status"] != "CHECKPOINTS_ACTIVE":
            raise RuntimeError(f"Cannot resume job {job_id} from {job['status']}")
        held_before -= FEE + BOND
        print(json.dumps({"event":"RESUMED","job":job,"totals":initial}, sort_keys=True), flush=True)

    replay_tx = ""
    if os.environ.get("CLEANCHECKPOINT_SKIP_REPLAY") != "1":
        replay_tx = submit(provider_account, "record_checkpoint", [job_id, "ARRIVAL", PROVIDER_URL, REPLAYED_DIGEST, 1])
        txs["replayed_checkpoint"] = replay_tx

        def replay_state():
            transaction = chain.get_transaction(replay_tx)
            checkpoints = int(read("get_totals")["checkpoints"])
            return {
                "ready": transaction.get("status_name") == "FINALIZED",
                "transaction": transaction,
                "checkpoints": checkpoints,
            }

        replay = wait("REPLAY_REJECTED", replay_state)
        if int(read("get_totals")["checkpoints"]) != checkpoint_before:
            raise RuntimeError("Replay mutated checkpoint state")
        leader = replay["transaction"].get("consensus_data", {}).get("leader_receipt", [{}])[0]
        rollback = leader.get("result", {})
        if leader.get("execution_result") != "ERROR" or rollback.get("status") != "rollback" or rollback.get("payload") != "EVIDENCE_ALREADY_USED":
            raise RuntimeError("Replay did not finalize as the expected EVIDENCE_ALREADY_USED rollback")
    else:
        print(json.dumps({"event":"REPLAY_SKIPPED","reason":"already proven in a prior finalized transaction"}), flush=True)

    txs["tampered_checkpoint"] = submit(provider_account, "record_checkpoint", [job_id, "COMPLETION", PROVIDER_URL, TAMPERED_DIGEST, 2])
    wait("TAMPER_COMMITTED", lambda: {"ready":int(read("get_totals")["checkpoints"]) == checkpoint_before + 1, "totals":read("get_totals")})
    txs["client_checkpoint"] = submit(client_account, "record_checkpoint", [job_id, "CLIENT_RESPONSE", TERMS_URL, TERMS_DIGEST, 1])
    wait("BOTH_SOURCES", lambda: {"ready":int(read("get_totals")["checkpoints"]) == checkpoint_before + 2, "totals":read("get_totals")})
    txs["open_dispute"] = submit(client_account, "open_dispute", [job_id])
    wait("DISPUTED", lambda: {"ready":read("get_job", [job_id])["status"] == "DISPUTED", "job":read("get_job", [job_id])})
    txs["adjudicate"] = submit(client_account, "adjudicate", [job_id])
    failed = wait("TAMPER_FAILED_CLOSED", lambda: {"ready":read("get_job", [job_id])["status"] == "RECOVERY" and read("get_job", [job_id])["integrity_status"] == "FAILED", "job":read("get_job", [job_id]), "totals":read("get_totals")})

    recovery_deadline = int(failed["job"]["recovery_deadline"])
    while int(time.time()) <= recovery_deadline:
        remaining = recovery_deadline - int(time.time()) + 1
        print(json.dumps({"event":"WAIT_RECOVERY_DEADLINE","seconds":remaining}), flush=True)
        time.sleep(min(30, remaining))
    txs["recover"] = submit(client_account, "recover", [job_id])
    final = wait("RECOVERED", lambda: {"ready":read("get_job", [job_id])["status"] == "SETTLED" and int(read("get_totals")["held"]) == held_before, "job":read("get_job", [job_id]), "totals":read("get_totals"), "contract_balance":int(chain.get_balance(ADDRESS))})
    totals = final["totals"]
    if int(totals["deposited"]) != int(totals["held"]) + int(totals["paid"]) + int(totals["refunded"]):
        raise RuntimeError("Conservation invariant failed")
    print(json.dumps({"event":"SECURITY_V2_FINAL","address":ADDRESS,"job_id":job_id,"replay_tx":replay_tx,"transactions":txs,"final":final}, sort_keys=True, default=str), flush=True)


if __name__ == "__main__":
    main()
