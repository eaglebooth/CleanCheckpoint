import json
import pytest

pytest.importorskip("gltest")
import gltest.direct.loader as direct_loader

CONTRACT_PATH = "contracts/CleanCheckpoint.py"
URL = "https://ipfs.io/ipfs/Qm" + ("a" * 44)
DIGEST = "sha256:" + ("a" * 64)


@pytest.fixture(autouse=True)
def _fd0_workaround(monkeypatch):
    original = direct_loader._inject_message_to_fd0

    def inject(vm):
        try:
            original(vm)
        except PermissionError:
            pass

    monkeypatch.setattr(direct_loader, "_inject_message_to_fd0", inject)


def _address(value):
    return "0x" + value.hex() if isinstance(value, bytes) else str(getattr(value, "as_hex", value))


def test_create_schedule_and_authoritative_readback(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm.sender = direct_owner
    contract = direct_deploy(CONTRACT_PATH)
    job_id = contract.create_job("Apartment reset", "HOME", _address(direct_alice), 10**16, URL, DIGEST)
    assert job_id == 0
    assert contract.set_schedule(job_id, 2_000_000_000, 2_000_000_100, 2_000_000_200) == "SCHEDULE_LOCKED"
    job = json.loads(contract.get_job(job_id))
    assert job["client"] == _address(direct_owner).lower()
    assert job["provider"] == _address(direct_alice).lower()
    assert job["status"] == "JOB_OPEN"
    assert job["service_deadline"] == 2_000_000_000


def test_roles_and_invalid_source_fail_before_mutation(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    direct_vm.sender = direct_owner
    contract = direct_deploy(CONTRACT_PATH)
    job_id = contract.create_job("Office reset", "OFFICE", _address(direct_alice), 10**16, URL, DIGEST)
    direct_vm.sender = direct_bob
    with pytest.raises(Exception):
        contract.set_schedule(job_id, 2_000_000_000, 2_000_000_100, 2_000_000_200)
    assert json.loads(contract.get_job(job_id))["service_deadline"] == 0
    direct_vm.sender = direct_owner
    with pytest.raises(Exception):
        contract.create_job("Bad evidence", "HOME", _address(direct_alice), 10**16, "https://example.com/editable", DIGEST)
    assert json.loads(contract.get_totals())["jobs"] == 1


def _funded_job(direct_vm, direct_deploy, client, provider):
    direct_vm.sender = client
    contract = direct_deploy(CONTRACT_PATH)
    job_id = contract.create_job("Apartment reset", "HOME", _address(provider), 10**16, URL, DIGEST)
    contract.set_schedule(job_id, 2_000_000_000, 2_000_000_100, 2_000_000_200)
    direct_vm.sender = provider
    direct_vm.value = 10**15
    assert contract.accept_job(job_id) == "PROVIDER_ACCEPTED"
    direct_vm.sender = client
    direct_vm.value = 10**16
    assert contract.fund_job(job_id) == "CHECKPOINTS_ACTIVE"
    direct_vm.value = 0
    return contract, job_id


def test_deterministic_happy_path_avoids_jury(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    assert contract.confirm_completion(job_id) == "FULL_PAYOUT"
    job = json.loads(contract.get_job(job_id))
    assert job["status"] == "SETTLED"
    assert job["verdict"] == "FULL_PAYOUT"
    assert job["provider_paid"] == 10**16
    assert job["provider_refunded"] == 10**15


def test_arrival_is_not_completion_evidence(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "ARRIVAL", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    with pytest.raises(Exception, match="PROVIDER_COMPLETION_REQUIRED"):
        contract.confirm_completion(job_id)


def test_dispute_jury_binds_facts_and_contract_derives_band(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    contract.record_checkpoint(job_id, "CLIENT_RESPONSE", "https://ipfs.io/ipfs/Qm" + ("b" * 44), "sha256:" + ("b" * 64), 1)
    assert contract.open_dispute(job_id) == "DISPUTED"
    direct_vm.mock_web(r".*", {"status": 200, "body": "Role-bound checkpoint evidence confirms partial completion."})
    direct_vm.mock_llm(r".*", json.dumps({"arrival": "YES", "completion": "PARTIAL", "client_response": "DISPUTED", "conflict": "NO"}))
    assert contract.adjudicate(job_id) == "PARTIAL_PAYOUT_50"
    job = json.loads(contract.get_job(job_id))
    assert job["status"] == "ADJUDICATED"
    assert job["verdict"] == "PARTIAL_PAYOUT_50"


def test_adjudication_uses_bound_completion_and_response_checkpoints(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    completion_url = "https://ipfs.io/ipfs/Qm" + ("c" * 44)
    later_url = "https://ipfs.io/ipfs/Qm" + ("d" * 44)
    response_url = "https://ipfs.io/ipfs/Qm" + ("e" * 44)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", completion_url, "sha256:" + ("c" * 64), 1)
    contract.record_checkpoint(job_id, "WORK_STARTED", later_url, "sha256:" + ("d" * 64), 2)
    direct_vm.sender = direct_owner
    contract.record_checkpoint(job_id, "CLIENT_RESPONSE", response_url, "sha256:" + ("e" * 64), 1)
    contract.open_dispute(job_id)
    direct_vm.mock_web(completion_url, {"status": 200, "body": "Completion record"})
    direct_vm.mock_web(later_url, {"status": 200, "body": "Later non-completion record"})
    direct_vm.mock_web(r".*", {"status": 200, "body": "Terms or client response"})
    direct_vm.mock_llm(r".*", json.dumps({"arrival": "YES", "completion": "FULL", "client_response": "DISPUTED", "conflict": "NO"}))
    assert contract.adjudicate(job_id) == "PARTIAL_PAYOUT_75"
    assert 0 in direct_vm._web_mocks_hit
    assert 1 not in direct_vm._web_mocks_hit


def _expire(contract, timestamp=2_000_000_300):
    contract._now = lambda: timestamp


def _totals(contract):
    return json.loads(contract.get_totals())


def test_provider_bond_exits_when_client_never_funds(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm.sender = direct_owner
    contract = direct_deploy(CONTRACT_PATH)
    job_id = contract.create_job("Apartment reset", "HOME", _address(direct_alice), 10**16, URL, DIGEST)
    contract.set_schedule(job_id, 2_000_000_000, 2_000_000_100, 2_000_000_200)
    direct_vm.sender = direct_alice
    direct_vm.value = 10**15
    contract.accept_job(job_id)
    direct_vm.value = 0
    _expire(contract)
    assert contract.recover(job_id) == "CLIENT_NON_FUNDING"
    job = json.loads(contract.get_job(job_id))
    assert job["provider_refunded"] == 10**15
    assert job["provider_paid"] == 0
    assert _totals(contract) == {"jobs": 1, "checkpoints": 0, "deposited": 10**15, "held": 0, "paid": 0, "refunded": 10**15}


def test_missing_provider_completion_protects_client_and_slashes_bond(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    _expire(contract)
    assert contract.recover(job_id) == "PROVIDER_COMPLETION_DEFAULT"
    job = json.loads(contract.get_job(job_id))
    assert job["client_refunded"] == 10**16
    assert job["client_paid"] == 10**15
    assert job["provider_refunded"] == 0
    assert _totals(contract)["held"] == 0
    assert _totals(contract)["paid"] == 10**15
    assert _totals(contract)["refunded"] == 10**16


def test_client_silence_after_completion_pays_provider(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    _expire(contract)
    assert contract.recover(job_id) == "CLIENT_RESPONSE_DEFAULT"
    job = json.loads(contract.get_job(job_id))
    assert job["provider_paid"] == 10**16
    assert job["provider_refunded"] == 10**15
    assert job["client_refunded"] == 0
    assert _totals(contract)["held"] == 0


def test_stalled_adjudication_returns_each_principal(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    contract.record_checkpoint(job_id, "CLIENT_RESPONSE", "https://ipfs.io/ipfs/Qm" + ("b" * 44), "sha256:" + ("b" * 64), 1)
    contract.open_dispute(job_id)
    _expire(contract)
    assert contract.recover(job_id) == "ADJUDICATION_TIMEOUT"
    job = json.loads(contract.get_job(job_id))
    assert job["provider_refunded"] == 10**15
    assert job["client_refunded"] == 10**16
    assert job["provider_paid"] == 0
    assert _totals(contract)["paid"] == 0
    assert _totals(contract)["refunded"] == 11 * 10**15


def test_both_evidence_without_terminal_action_returns_each_principal(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    contract.record_checkpoint(job_id, "CLIENT_RESPONSE", "https://ipfs.io/ipfs/Qm" + ("b" * 44), "sha256:" + ("b" * 64), 1)
    _expire(contract)
    assert contract.recover(job_id) == "EVIDENCE_RECOVERY"
    job = json.loads(contract.get_job(job_id))
    assert job["provider_refunded"] == 10**15
    assert job["client_refunded"] == 10**16
    assert _totals(contract)["held"] == 0


def test_recovery_rejects_early_outsider_and_repeat(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    contract._now = lambda: 1_999_999_999
    with pytest.raises(Exception, match="RECOVERY_NOT_DUE"):
        contract.recover(job_id)
    direct_vm.sender = direct_bob
    _expire(contract)
    with pytest.raises(Exception, match="PARTY_ONLY"):
        contract.recover(job_id)
    direct_vm.sender = direct_owner
    assert contract.recover(job_id) == "PROVIDER_COMPLETION_DEFAULT"
    with pytest.raises(Exception, match="NOT_RECOVERABLE"):
        contract.recover(job_id)


def test_evidence_conflict_recovery_returns_each_principal(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    contract.record_checkpoint(job_id, "CLIENT_RESPONSE", "https://ipfs.io/ipfs/Qm" + ("b" * 44), "sha256:" + ("b" * 64), 1)
    contract.open_dispute(job_id)
    direct_vm.mock_web(r".*", {"status": 200, "body": "Evidence cannot be reconciled."})
    direct_vm.mock_llm(r".*", json.dumps({"arrival": "UNVERIFIED", "completion": "UNVERIFIED", "client_response": "UNVERIFIED", "conflict": "YES"}))
    assert contract.adjudicate(job_id) == "EVIDENCE_CONFLICT"
    assert json.loads(contract.get_job(job_id))["status"] == "RECOVERY"
    _expire(contract)
    assert contract.recover(job_id) == "EVIDENCE_RECOVERY"
    totals = _totals(contract)
    assert totals["held"] == 0
    assert totals["paid"] == 0
    assert totals["refunded"] == totals["deposited"] == 11 * 10**15


def test_adjudicated_timeout_router_executes_locked_verdict(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    direct_vm.sender = direct_alice
    contract.record_checkpoint(job_id, "COMPLETION", URL, DIGEST, 1)
    direct_vm.sender = direct_owner
    contract.record_checkpoint(job_id, "CLIENT_RESPONSE", "https://ipfs.io/ipfs/Qm" + ("b" * 44), "sha256:" + ("b" * 64), 1)
    contract.open_dispute(job_id)
    direct_vm.mock_web(r".*", {"status": 200, "body": "Partial completion is consistently documented."})
    direct_vm.mock_llm(r".*", json.dumps({"arrival": "YES", "completion": "PARTIAL", "client_response": "DISPUTED", "conflict": "NO"}))
    assert contract.adjudicate(job_id) == "PARTIAL_PAYOUT_50"
    assert contract.recover(job_id) == "PARTIAL_PAYOUT_50"
    job = json.loads(contract.get_job(job_id))
    assert job["status"] == "SETTLED"
    assert job["provider_paid"] == 5 * 10**15
    assert job["provider_refunded"] == 10**15
    assert job["client_refunded"] == 5 * 10**15


def test_deadline_entry_points_fail_closed(direct_vm, direct_deploy, direct_owner, direct_alice):
    direct_vm.sender = direct_owner
    contract = direct_deploy(CONTRACT_PATH)
    job_id = contract.create_job("Apartment reset", "HOME", _address(direct_alice), 10**16, URL, DIGEST)
    contract.set_schedule(job_id, 2_000_000_000, 2_000_000_100, 2_000_000_200)
    _expire(contract)
    direct_vm.sender = direct_alice
    direct_vm.value = 10**15
    with pytest.raises(Exception, match="ACCEPTANCE_CLOSED"):
        contract.accept_job(job_id)

    direct_vm.sender = direct_owner
    second_id = contract.create_job("Office reset", "OFFICE", _address(direct_alice), 10**16, URL, DIGEST)
    contract._now = lambda: 1_900_000_000
    contract.set_schedule(second_id, 2_000_000_000, 2_000_000_100, 2_000_000_200)
    direct_vm.sender = direct_alice
    direct_vm.value = 10**15
    contract.accept_job(second_id)
    direct_vm.sender = direct_owner
    direct_vm.value = 10**16
    _expire(contract)
    with pytest.raises(Exception, match="FUNDING_CLOSED"):
        contract.fund_job(second_id)
    assert json.loads(contract.get_job(second_id))["status"] == "PROVIDER_ACCEPTED"


def test_value_conservation_for_every_terminal_timeout(direct_vm, direct_deploy, direct_owner, direct_alice):
    contract, job_id = _funded_job(direct_vm, direct_deploy, direct_owner, direct_alice)
    _expire(contract)
    contract.recover(job_id)
    totals = _totals(contract)
    assert totals["deposited"] == totals["held"] + totals["paid"] + totals["refunded"]
