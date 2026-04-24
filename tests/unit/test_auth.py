# tests/test_auth.py

import uuid
import pytest
from tests.conftest import _seed_user, get_token, auth


# ── login ──────────────────────────────────────────────────────────────────────

def test_login_success(client, db):
    _seed_user(db, "user@kerna.in", "pass123")
    resp = client.post("/auth/login", json={"email": "user@kerna.in", "password": "pass123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 10


def test_login_wrong_password(client, db):
    _seed_user(db, "user@kerna.in", "correctpass")
    resp = client.post("/auth/login", json={"email": "user@kerna.in", "password": "wrongpass"})
    assert resp.status_code == 422


def test_login_unknown_email(client):
    resp = client.post("/auth/login", json={"email": "ghost@nowhere.com", "password": "x"})
    assert resp.status_code == 422


def test_login_missing_email(client):
    resp = client.post("/auth/login", json={"password": "secret"})
    assert resp.status_code == 422


def test_login_missing_password(client):
    resp = client.post("/auth/login", json={"email": "user@kerna.in"})
    assert resp.status_code == 422


def test_login_empty_body(client):
    resp = client.post("/auth/login", json={})
    assert resp.status_code == 422


def test_login_inactive_user(client, db):
    """Inactive user should not get token — assumption: service checks active flag."""
    user = _seed_user(db, "inactive@kerna.in", "pass")
    user.active = False
    db.commit()
    resp = client.post("/auth/login", json={"email": "inactive@kerna.in", "password": "pass"})
    # expect 401 or 422 depending on service implementation
    assert resp.status_code in (401, 422)


# ── protected route without token ─────────────────────────────────────────────

def test_no_token_leads_list_returns_401(client):
    resp = client.get("/leads/")
    assert resp.status_code == 401


def test_no_token_create_lead_returns_401(client):
    resp = client.post("/leads/", json={
        "company_name": "X", "contact_name": "Y", "email": "y@x.com", "phone": "0",
    })
    assert resp.status_code == 401


def test_no_token_quotation_returns_401(client):
    resp = client.post("/quotations/", json={"lead_id": str(uuid.uuid4())})
    assert resp.status_code == 401


def test_no_token_approvals_returns_401(client):
    resp = client.post(f"/approvals/versions/{uuid.uuid4()}/request")
    assert resp.status_code == 401


def test_garbage_token_returns_401(client):
    resp = client.get("/leads/", headers={"Authorization": "Bearer garbage.token.here"})
    assert resp.status_code == 401


def test_malformed_auth_header_returns_401(client):
    resp = client.get("/leads/", headers={"Authorization": "NotBearer sometoken"})
    assert resp.status_code in (401, 403)


# ── protected route with valid token ──────────────────────────────────────────

def test_valid_token_leads_accessible(client, db):
    _seed_user(db, "poc@kerna.in", "pass")
    token = get_token(client, "poc@kerna.in", "pass")
    resp = client.get("/leads/", headers=auth(token))
    assert resp.status_code == 200


def test_valid_token_create_lead_works(client, db):
    _seed_user(db, "poc@kerna.in", "pass")
    token = get_token(client, "poc@kerna.in", "pass")
    resp = client.post("/leads/", json={
        "company_name": "Acme", "contact_name": "Bob",
        "email": "bob@acme.com", "phone": "9000000001",
    }, headers=auth(token))
    assert resp.status_code == 200


def test_token_from_one_user_works_independently(client, db):
    """Two users get separate tokens — both valid."""
    _seed_user(db, "a@kerna.in", "passA")
    _seed_user(db, "b@kerna.in", "passB")
    tok_a = get_token(client, "a@kerna.in", "passA")
    tok_b = get_token(client, "b@kerna.in", "passB")
    assert tok_a != tok_b
    for tok in (tok_a, tok_b):
        assert client.get("/leads/", headers=auth(tok)).status_code == 200
