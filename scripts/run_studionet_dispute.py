"""CleanCheckpoint public-evidence dispute lifecycle on Studionet."""

import json
import os
import time

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


ADDRESS = "0x9bC7649FA843E5FFa4E6f63E2b392D0071E86016"
RPC_URL = "https://studio.genlayer.com/api"
FEE = 10**16
BOND = 10**15
TERMS_URL = "https://gateway.pinata.cloud/ipfs/QmQBQDCyfCNC63GBDCSP7WfTNBkTSWSRpUg4Hr7aZjAdKH"
TERMS_DIGEST = "sha256:03d4c0e4185b0a7da060a9f1efc0e29cf6e6d3cc9ae3030de56de7c754873cff"
PROVIDER_URL = "https://gateway.pinata.cloud/ipfs/QmWzpoMsDRrAWfWaLoY21QmwsStcYY8Z66k8yvG8rGsfgP"
PROVIDER_DIGEST = "sha256:c9dee431e40daf70e2ac0ebe94d3585356ee6677990f3a2687ae09cbfae20719"
CLIENT_URL = "https://gateway.pinata.cloud/ipfs/QmeGVuNHeq9Vs21QSRFzNW3TxR19eXijfbropBteGdP1To"
CLIENT_DIGEST = "sha256:1eb2a75bdc6bce174d6f06df3f05117fad0ee35222d5106e32e9b664d60a0ba2"


def parse(value):
    return json.loads(value) if isinstance(value, str) else value


def main():
    client_key = os.environ.get("CLEANCHECKPOINT_CLIENT_PRIVATE_KEY", "")
    provider_key = os.environ.get("CLEANCHECKPOINT_PROVIDER_PRIVATE_KEY", "")
    if not client_key or not provider_key:
        raise RuntimeError("Set both CleanCheckpoint test key environment variables.")
    client_account = create_account(client_key)
    provider_account = create_account(provider_key)
    chain = create_client(chain=studionet, account=client_account, endpoint=RPC_URL)

    def read(name, args=None):
        return parse(chain.read_contract(address=ADDRESS, function_name=name, args=args or [], account=client_account))

    def submit(account, method, args, value=0):
        tx_hash = str(chain.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value))
        print(json.dumps({"event": "TX_SUBMITTED", "method": method, "tx": tx_hash}, sort_keys=True), flush=True)
        return tx_hash

    def wait_for(label, predicate, timeout=720):
        deadline = time.time() + timeout
        last = ""
        while time.time() < deadline:
            state = predicate()
            encoded = json.dumps(state, sort_keys=True, default=str)
            if encoded != last:
                print(json.dumps({"event": label, "state": state}, sort_keys=True, default=str), flush=True)
                last = encoded
            if state.get("ready"):
                return state
            time.sleep(5)
        raise TimeoutError(label + " did not reach expected state")

    initial = read("get_totals")
    job_id = int(initial["jobs"])
    initial_checkpoints = int(initial["checkpoints"])
    held_before = int(initial["held"])
    contract_before = int(chain.get_balance(ADDRESS))
    provider_before = int(chain.get_balance(provider_account.address))
    client_before = int(chain.get_balance(client_account.address))
    transactions = {}
    print(json.dumps({"event": "START", "job_id": job_id, "initial": initial}, sort_keys=True), flush=True)

    transactions["create_job"] = submit(client_account, "create_job", ["Public evidence dispute " + str(job_id), "HOME", provider_account.address, FEE, TERMS_URL, TERMS_DIGEST])
    wait_for("JOB_CREATED", lambda: {"ready": int(read("get_totals")["jobs"]) > job_id, "totals": read("get_totals")})

    now = int(time.time())
    transactions["set_schedule"] = submit(client_account, "set_schedule", [job_id, now + 3600, now + 7200, now + 10800])
    wait_for("SCHEDULE_LOCKED", lambda: {"ready": int(read("get_job", [job_id])["service_deadline"]) > now, "job": read("get_job", [job_id])})

    transactions["accept_job"] = submit(provider_account, "accept_job", [job_id], BOND)
    wait_for("PROVIDER_ACCEPTED", lambda: {"ready": read("get_job", [job_id])["status"] == "PROVIDER_ACCEPTED", "job": read("get_job", [job_id])})

    transactions["fund_job"] = submit(client_account, "fund_job", [job_id], FEE)
    wait_for("CUSTODY", lambda: {
        "ready": read("get_job", [job_id])["status"] == "CHECKPOINTS_ACTIVE"
        and int(read("get_totals")["held"]) == held_before + FEE + BOND,
        "job": read("get_job", [job_id]), "totals": read("get_totals"), "contract_balance": int(chain.get_balance(ADDRESS)),
    })

    transactions["provider_checkpoint"] = submit(provider_account, "record_checkpoint", [job_id, "COMPLETION", PROVIDER_URL, PROVIDER_DIGEST, 1])
    wait_for("PROVIDER_EVIDENCE", lambda: {"ready": int(read("get_totals")["checkpoints"]) > initial_checkpoints, "totals": read("get_totals")})

    transactions["client_checkpoint"] = submit(client_account, "record_checkpoint", [job_id, "CLIENT_RESPONSE", CLIENT_URL, CLIENT_DIGEST, 1])
    wait_for("BOTH_EVIDENCE", lambda: {"ready": int(read("get_totals")["checkpoints"]) > initial_checkpoints + 1, "totals": read("get_totals")})

    transactions["open_dispute"] = submit(client_account, "open_dispute", [job_id])
    wait_for("DISPUTED", lambda: {"ready": read("get_job", [job_id])["status"] == "DISPUTED", "job": read("get_job", [job_id])})

    transactions["adjudicate"] = submit(client_account, "adjudicate", [job_id])
    adjudicated = wait_for("JURY_RESULT", lambda: {
        "ready": read("get_job", [job_id])["status"] in ("ADJUDICATED", "RECOVERY"),
        "job": read("get_job", [job_id]),
    }, timeout=900)

    verdict = adjudicated["job"]["verdict"]
    if adjudicated["job"]["status"] != "ADJUDICATED":
        raise RuntimeError("Jury routed to recovery with verdict " + verdict)
    if verdict != "PARTIAL_PAYOUT_75":
        raise RuntimeError("Unexpected bounded verdict: " + verdict)

    transactions["settle"] = submit(client_account, "settle", [job_id])
    expected_provider = FEE * 75 // 100
    expected_client = FEE - (FEE * 75 // 100)
    final = wait_for("PARTIAL_SETTLEMENT", lambda: {
        "ready": read("get_job", [job_id])["status"] == "SETTLED"
        and int(read("get_job", [job_id])["provider_paid"]) == expected_provider
        and int(read("get_job", [job_id])["provider_refunded"]) == BOND
        and int(read("get_job", [job_id])["client_refunded"]) == expected_client
        and int(read("get_totals")["held"]) == held_before
        and int(chain.get_balance(ADDRESS)) == contract_before,
        "job": read("get_job", [job_id]), "totals": read("get_totals"), "contract_balance": int(chain.get_balance(ADDRESS)),
    }, timeout=720)

    tx_results = {}
    for name, tx_hash in transactions.items():
        tx = chain.get_transaction(tx_hash)
        tx_results[name] = {"hash": tx_hash, "status": tx.get("status_name"), "result": tx.get("result_name"), "execution": tx.get("tx_execution_result_name")}

    print(json.dumps({
        "event": "FINAL_RESULT", "job_id": job_id, "verdict": verdict,
        "final": final, "transactions": tx_results,
        "provider_expected": expected_provider, "client_expected": expected_client,
        "provider_balance_before": provider_before, "provider_balance_after": int(chain.get_balance(provider_account.address)),
        "client_balance_before": client_before, "client_balance_after": int(chain.get_balance(client_account.address)),
    }, sort_keys=True, default=str), flush=True)


if __name__ == "__main__":
    main()
