# tests/test_approvals.py

import uuid
import pytest
from tests.conftest import _seed_user, get_token, auth


# ── helpers ────────────────────────────────────────────────────────────────────

def _upload_version(client, headers, module_id):
    r = client.post(f"/modules/{module_id}/versions", json={
        "file_url": "https://cdn.kerna.in/v.zip",
        "notes": "test",
    }, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _request(client, headers, version_id):
    r = client.post(f"/approvals/versions/{version_id}/request", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


# ── 401 guards ─────────────────────────────────────────────────────────────────

def test_request_approval_no_token(client):
    assert client.post(f"/approvals/versions/{uuid.uuid4()}/request").status_code == 401


def test_approve_no_token(client):
    assert client.post(f"/approvals/{uuid.uuid4()}/approve",
                       json={"user_id": str(uuid.uuid4())}).status_code == 401


def test_reject_no_token(client):
    assert client.post(f"/approvals/{uuid.uuid4()}/reject",
                       json={"user_id": str(uuid.uuid4())}).status_code == 401


def test_withdraw_no_token(client):
    assert client.post(f"/approvals/{uuid.uuid4()}/withdraw",
                       json={"user_id": str(uuid.uuid4())}).status_code == 401


# ── request ────────────────────────────────────────────────────────────────────

def test_request_approval_success(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    resp = client.post(f"/approvals/versions/{v_id}/request", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PENDING"
    assert data["module_version_id"] == v_id
    assert data["lock_expires_at"] is not None


def test_request_version_not_found(client, headers):
    assert client.post(f"/approvals/versions/{uuid.uuid4()}/request",
                       headers=headers).status_code == 404


def test_request_duplicate_fails(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    client.post(f"/approvals/versions/{v_id}/request", headers=headers)
    resp = client.post(f"/approvals/versions/{v_id}/request", headers=headers)
    assert resp.status_code == 422


# ── approve ────────────────────────────────────────────────────────────────────

def test_approve_success(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)

    resp = client.post(f"/approvals/{appr['id']}/approve",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "APPROVED"
    assert data["approved_by"] == str(founder_user.id)
    assert data["approved_at"] is not None


def test_approve_already_approved_fails(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    uid = str(founder_user.id)
    client.post(f"/approvals/{appr['id']}/approve", json={"user_id": uid}, headers=headers)
    resp = client.post(f"/approvals/{appr['id']}/approve", json={"user_id": uid}, headers=headers)
    assert resp.status_code == 422


def test_approve_rejected_fails(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    uid = str(founder_user.id)
    client.post(f"/approvals/{appr['id']}/reject", json={"user_id": uid}, headers=headers)
    resp = client.post(f"/approvals/{appr['id']}/approve", json={"user_id": uid}, headers=headers)
    assert resp.status_code == 422


def test_approve_not_found(client, headers, founder_user):
    assert client.post(f"/approvals/{uuid.uuid4()}/approve",
                       json={"user_id": str(founder_user.id)}, headers=headers).status_code == 404


def test_approve_missing_user_id(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    assert client.post(f"/approvals/{appr['id']}/approve",
                       json={}, headers=headers).status_code == 422


def test_approve_invalid_user_id(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    assert client.post(f"/approvals/{appr['id']}/approve",
                       json={"user_id": "bad"}, headers=headers).status_code == 422


# ── reject ─────────────────────────────────────────────────────────────────────

def test_reject_success(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)

    resp = client.post(f"/approvals/{appr['id']}/reject",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "REJECTED"


def test_reject_already_approved_fails(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    uid = str(founder_user.id)
    client.post(f"/approvals/{appr['id']}/approve", json={"user_id": uid}, headers=headers)
    resp = client.post(f"/approvals/{appr['id']}/reject", json={"user_id": uid}, headers=headers)
    assert resp.status_code == 422


def test_reject_missing_user_id(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    assert client.post(f"/approvals/{appr['id']}/reject",
                       json={}, headers=headers).status_code == 422


def test_reject_not_found(client, headers, founder_user):
    assert client.post(f"/approvals/{uuid.uuid4()}/reject",
                       json={"user_id": str(founder_user.id)}, headers=headers).status_code == 404


# ── withdraw ───────────────────────────────────────────────────────────────────

def test_withdraw_success(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)

    resp = client.post(f"/approvals/{appr['id']}/withdraw",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # status stays PENDING — withdraw does NOT change status (architecture rule)
    assert data["status"] == "PENDING"
    assert data["withdrawn_at"] is not None
    assert data["withdrawn_by"] == str(founder_user.id)


def test_withdraw_approved_fails(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    uid = str(founder_user.id)
    client.post(f"/approvals/{appr['id']}/approve", json={"user_id": uid}, headers=headers)
    resp = client.post(f"/approvals/{appr['id']}/withdraw", json={"user_id": uid}, headers=headers)
    assert resp.status_code == 422


def test_withdraw_rejected_fails(client, headers, seed_module, founder_user):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    uid = str(founder_user.id)
    client.post(f"/approvals/{appr['id']}/reject", json={"user_id": uid}, headers=headers)
    resp = client.post(f"/approvals/{appr['id']}/withdraw", json={"user_id": uid}, headers=headers)
    assert resp.status_code == 422


def test_withdraw_missing_user_id(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    assert client.post(f"/approvals/{appr['id']}/withdraw",
                       json={}, headers=headers).status_code == 422


def test_withdraw_invalid_user_id(client, headers, seed_module):
    v_id = _upload_version(client, headers, seed_module["id"])
    appr = _request(client, headers, v_id)
    assert client.post(f"/approvals/{appr['id']}/withdraw",
                       json={"user_id": "bad-uuid"}, headers=headers).status_code == 422


def test_withdraw_not_found(client, headers, founder_user):
    assert client.post(f"/approvals/{uuid.uuid4()}/withdraw",
                       json={"user_id": str(founder_user.id)}, headers=headers).status_code == 404


# ── cross-version isolation ────────────────────────────────────────────────────

def test_two_versions_independent_approvals(client, headers, seed_module, founder_user):
    uid = str(founder_user.id)
    v1 = _upload_version(client, headers, seed_module["id"])
    v2 = _upload_version(client, headers, seed_module["id"])
    a1 = _request(client, headers, v1)
    a2 = _request(client, headers, v2)
    assert a1["id"] != a2["id"]

    r1 = client.post(f"/approvals/{a1['id']}/approve", json={"user_id": uid}, headers=headers)
    r2 = client.post(f"/approvals/{a2['id']}/reject", json={"user_id": uid}, headers=headers)
    assert r1.json()["status"] == "APPROVED"
    assert r2.json()["status"] == "REJECTED"


# ── token from a different valid user still works (no role guard yet) ──────────

def test_second_user_token_can_request_approval(client, db, headers, seed_module):
    _seed_user(db, "dev2@kerna.in", "devpass")
    tok2 = get_token(client, "dev2@kerna.in", "devpass")
    v_id = _upload_version(client, headers, seed_module["id"])
    resp = client.post(f"/approvals/versions/{v_id}/request", headers=auth(tok2))
    assert resp.status_code == 200
