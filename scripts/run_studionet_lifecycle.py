"""CleanCheckpoint two-wallet Studionet custody happy path.

Private keys are read only from process environment and are never persisted.
"""

import json
import os
import time

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


ADDRESS = "0x6e2A785B1699067F8573e765B601f651917D7e47"
RPC_URL = "https://studio.genlayer.com/api"
FEE = 10**16
BOND = 10**15
URL = "https://ipfs.io/ipfs/QmbbFBJ3zdfjdPEXaAa6wNrPNnX6Cm4WENSbysAoCjhe8F"
DIGEST = "sha256:" + ("1" * 64)


def parse(value):
    return json.loads(value) if isinstance(value, str) else value


def main():
    client_key = os.environ.get("CLEANCHECKPOINT_CLIENT_PRIVATE_KEY", "")
    provider_key = os.environ.get("CLEANCHECKPOINT_PROVIDER_PRIVATE_KEY", "")
    if not client_key or not provider_key:
        raise RuntimeError("Set both CleanCheckpoint test key environment variables.")

    client_account = create_account(client_key)
    provider_account = create_account(provider_key)
    if client_account.address.lower() == provider_account.address.lower():
        raise RuntimeError("Client and provider must be different wallets.")

    chain = create_client(chain=studionet, account=client_account, endpoint=RPC_URL)

    def read(name, args=None):
        return parse(chain.read_contract(address=ADDRESS, function_name=name, args=args or [], account=client_account))

    def submit(account, method, args, value=0):
        tx = chain.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value)
        tx_hash = str(tx)
        print(json.dumps({"event": "TX_SUBMITTED", "method": method, "tx": tx_hash}, sort_keys=True), flush=True)
        return tx_hash

    def wait_for(label, predicate, timeout=480):
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
    held_before = int(initial["held"])
    contract_before = int(chain.get_balance(ADDRESS))
    provider_before = int(chain.get_balance(provider_account.address))
    print(json.dumps({
        "event": "START", "job_id": job_id, "client": client_account.address,
        "provider": provider_account.address, "contract_balance": contract_before,
        "totals": initial,
    }, sort_keys=True), flush=True)

    transactions = {}
    transactions["create_job"] = submit(client_account, "create_job", [
        "Studionet checkpoint payout " + str(job_id), "HOME", provider_account.address,
        FEE, URL, DIGEST,
    ])
    wait_for("JOB_CREATED", lambda: {"ready": int(read("get_totals")["jobs"]) > job_id, "totals": read("get_totals")})

    now = int(time.time())
    transactions["set_schedule"] = submit(client_account, "set_schedule", [job_id, now + 3600, now + 7200, now + 10800])
    wait_for("SCHEDULE_LOCKED", lambda: {"ready": int(read("get_job", [job_id])["service_deadline"]) > now, "job": read("get_job", [job_id])})

    transactions["accept_job"] = submit(provider_account, "accept_job", [job_id], BOND)
    wait_for("BOND_HELD", lambda: {
        "ready": read("get_job", [job_id])["status"] == "PROVIDER_ACCEPTED"
        and int(read("get_totals")["held"]) == held_before + BOND,
        "job": read("get_job", [job_id]), "totals": read("get_totals"),
        "contract_balance": int(chain.get_balance(ADDRESS)),
    })

    transactions["fund_job"] = submit(client_account, "fund_job", [job_id], FEE)
    custody = wait_for("FULL_CUSTODY", lambda: {
        "ready": read("get_job", [job_id])["status"] == "CHECKPOINTS_ACTIVE"
        and int(read("get_totals")["held"]) == held_before + FEE + BOND
        and int(chain.get_balance(ADDRESS)) >= contract_before + FEE + BOND,
        "job": read("get_job", [job_id]), "totals": read("get_totals"),
        "contract_balance": int(chain.get_balance(ADDRESS)),
    })

    transactions["record_checkpoint"] = submit(provider_account, "record_checkpoint", [job_id, "COMPLETION", URL, DIGEST, 1])
    wait_for("PROVIDER_CHECKPOINT", lambda: {"ready": int(read("get_totals")["checkpoints"]) > int(initial["checkpoints"]), "totals": read("get_totals")})

    transactions["confirm_completion"] = submit(client_account, "confirm_completion", [job_id])
    final = wait_for("PAYOUT_SETTLED", lambda: {
        "ready": read("get_job", [job_id])["status"] == "SETTLED"
        and read("get_job", [job_id])["verdict"] == "FULL_PAYOUT"
        and int(read("get_job", [job_id])["provider_paid"]) == FEE + BOND
        and int(read("get_totals")["held"]) == held_before
        and int(chain.get_balance(ADDRESS)) == contract_before,
        "job": read("get_job", [job_id]), "totals": read("get_totals"),
        "contract_balance": int(chain.get_balance(ADDRESS)),
    })

    tx_results = {}
    for name, tx_hash in transactions.items():
        tx = chain.get_transaction(tx_hash)
        tx_results[name] = {
            "hash": tx_hash,
            "status": tx.get("status_name"),
            "result": tx.get("result_name"),
            "execution": tx.get("tx_execution_result_name"),
        }

    print(json.dumps({
        "event": "FINAL_RESULT", "address": ADDRESS, "job_id": job_id,
        "custody": custody, "final": final, "transactions": tx_results,
        "provider_balance_before": provider_before,
        "provider_balance_after": int(chain.get_balance(provider_account.address)),
    }, sort_keys=True, default=str), flush=True)


if __name__ == "__main__":
    main()
