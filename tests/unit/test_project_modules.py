# tests/test_project_modules.py

import uuid
import pytest
from tests.conftest import _seed_user, get_token, auth


# ── 401 guards ─────────────────────────────────────────────────────────────────

def test_create_module_no_token(client, seed_project):
    assert client.post(f"/projects/{seed_project['id']}/modules",
                       json={"module_type": "DEV"}).status_code == 401


def test_list_modules_no_token(client, seed_project):
    assert client.get(f"/projects/{seed_project['id']}/modules").status_code == 401


def test_assign_user_no_token(client, seed_module):
    assert client.post(f"/modules/{seed_module['id']}/assign",
                       json={"user_id": str(uuid.uuid4())}).status_code == 401


def test_update_status_no_token(client, seed_module):
    assert client.patch(f"/modules/{seed_module['id']}/status",
                        json={"status": "IN_PROGRESS"}).status_code == 401


# ── create ─────────────────────────────────────────────────────────────────────

def test_create_module_success(client, headers, seed_project):
    resp = client.post(f"/projects/{seed_project['id']}/modules",
                       json={"module_type": "DEV"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["module_type"] == "DEV"
    assert data["project_id"] == seed_project["id"]


def test_create_module_missing_type(client, headers, seed_project):
    resp = client.post(f"/projects/{seed_project['id']}/modules",
                       json={}, headers=headers)
    assert resp.status_code == 422


def test_create_module_project_not_found(client, headers):
    resp = client.post(f"/projects/{uuid.uuid4()}/modules",
                       json={"module_type": "DEV"}, headers=headers)
    assert resp.status_code == 404


def test_create_multiple_module_types(client, headers, seed_project):
    p_id = seed_project["id"]
    for mtype in ["DEV", "DESIGN", "CONTENT"]:
        r = client.post(f"/projects/{p_id}/modules",
                        json={"module_type": mtype}, headers=headers)
        assert r.status_code == 200, f"{mtype} failed"


# ── list ───────────────────────────────────────────────────────────────────────

def test_list_modules_empty(client, headers, seed_project):
    resp = client.get(f"/projects/{seed_project['id']}/modules", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_modules_returns_created(client, headers, seed_module, seed_project):
    resp = client.get(f"/projects/{seed_project['id']}/modules", headers=headers)
    assert resp.status_code == 200
    assert any(m["id"] == seed_module["id"] for m in resp.json())


# ── update status ──────────────────────────────────────────────────────────────

def test_update_status_success(client, headers, seed_module):
    resp = client.patch(f"/modules/{seed_module['id']}/status",
                        json={"status": "IN_PROGRESS"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"


def test_update_status_invalid(client, headers, seed_module):
    resp = client.patch(f"/modules/{seed_module['id']}/status",
                        json={"status": "FLYING"}, headers=headers)
    assert resp.status_code == 422


def test_update_status_missing_field(client, headers, seed_module):
    resp = client.patch(f"/modules/{seed_module['id']}/status",
                        json={}, headers=headers)
    assert resp.status_code == 422


def test_update_status_not_found(client, headers):
    assert client.patch(f"/modules/{uuid.uuid4()}/status",
                        json={"status": "IN_PROGRESS"}, headers=headers).status_code == 404


# ── assign user ────────────────────────────────────────────────────────────────

def test_assign_user_success(client, headers, seed_module, founder_user):
    resp = client.post(f"/modules/{seed_module['id']}/assign",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 200


def test_assign_user_duplicate_fails(client, headers, seed_module, founder_user):
    payload = {"user_id": str(founder_user.id)}
    client.post(f"/modules/{seed_module['id']}/assign", json=payload, headers=headers)
    resp = client.post(f"/modules/{seed_module['id']}/assign", json=payload, headers=headers)
    assert resp.status_code == 422


def test_assign_user_invalid_uuid(client, headers, seed_module):
    resp = client.post(f"/modules/{seed_module['id']}/assign",
                       json={"user_id": "bad-id"}, headers=headers)
    assert resp.status_code == 422


def test_assign_user_module_not_found(client, headers, founder_user):
    resp = client.post(f"/modules/{uuid.uuid4()}/assign",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 404


def test_assign_user_missing_user_id(client, headers, seed_module):
    resp = client.post(f"/modules/{seed_module['id']}/assign", json={}, headers=headers)
    assert resp.status_code == 422


# ── unassign ───────────────────────────────────────────────────────────────────

def test_unassign_user_success(client, headers, seed_module, founder_user):
    uid = str(founder_user.id)
    client.post(f"/modules/{seed_module['id']}/assign", json={"user_id": uid}, headers=headers)
    resp = client.post(f"/modules/{seed_module['id']}/unassign",
                       json={"user_id": uid}, headers=headers)
    assert resp.status_code == 200


def test_unassign_user_not_assigned_fails(client, headers, seed_module, founder_user):
    resp = client.post(f"/modules/{seed_module['id']}/unassign",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 404


# ── list assignments ───────────────────────────────────────────────────────────

def test_list_assignments(client, headers, seed_module, founder_user):
    uid = str(founder_user.id)
    client.post(f"/modules/{seed_module['id']}/assign", json={"user_id": uid}, headers=headers)
    resp = client.get(f"/modules/{seed_module['id']}/assignments", headers=headers)
    assert resp.status_code == 200
    assert any(a["user_id"] == uid for a in resp.json())


def test_list_assignments_no_token(client, seed_module):
    assert client.get(f"/modules/{seed_module['id']}/assignments").status_code == 401


# ── RBAC — different user token still allowed (no role enforcement yet) ────────

def test_different_user_token_can_read_modules(client, db, headers, seed_project):
    """Second user with valid token can list modules — role enforcement comes later."""
    _seed_user(db, "dev@kerna.in", "devpass")
    dev_token = get_token(client, "dev@kerna.in", "devpass")
    resp = client.get(f"/projects/{seed_project['id']}/modules", headers=auth(dev_token))
    assert resp.status_code == 200
