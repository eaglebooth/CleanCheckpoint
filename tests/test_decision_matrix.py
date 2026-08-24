def derive(arrival, completion, response, conflict):
    if conflict == "YES" or "UNVERIFIED" in (arrival, completion, response):
        return "EVIDENCE_CONFLICT"
    if arrival == "NO" or completion == "NONE":
        return "CLIENT_REFUND"
    if completion == "FULL" and response == "ACCEPTED":
        return "FULL_PAYOUT"
    if completion == "FULL":
        return "PARTIAL_PAYOUT_75"
    return "PARTIAL_PAYOUT_50"


def test_precedence_and_happy_path():
    assert derive("YES", "FULL", "ACCEPTED", "NO") == "FULL_PAYOUT"
    assert derive("NO", "FULL", "ACCEPTED", "NO") == "CLIENT_REFUND"
    assert derive("YES", "FULL", "ACCEPTED", "YES") == "EVIDENCE_CONFLICT"
    assert derive("UNVERIFIED", "FULL", "ACCEPTED", "NO") == "EVIDENCE_CONFLICT"


def test_partial_bands():
    assert derive("YES", "FULL", "DISPUTED", "NO") == "PARTIAL_PAYOUT_75"
    assert derive("YES", "PARTIAL", "DISPUTED", "NO") == "PARTIAL_PAYOUT_50"


def signature(facts):
    return "|".join(facts[key] for key in ("arrival", "completion", "client_response", "conflict"))


def test_each_consequential_field_is_differentially_bound():
    base = {"arrival": "YES", "completion": "FULL", "client_response": "ACCEPTED", "conflict": "NO"}
    alternatives = {"arrival": "NO", "completion": "PARTIAL", "client_response": "DISPUTED", "conflict": "YES"}
    for field, replacement in alternatives.items():
        changed = dict(base)
        changed[field] = replacement
        assert signature(changed) != signature(base)
