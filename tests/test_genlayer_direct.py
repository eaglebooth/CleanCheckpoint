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
    assert job["provider_paid"] == 11 * 10**15


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
