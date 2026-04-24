# tests/test_leads.py

import uuid
import pytest
from tests.conftest import _seed_user, get_token, auth


# ── 401 guards ─────────────────────────────────────────────────────────────────

def test_list_leads_no_token(client):
    assert client.get("/leads/").status_code == 401


def test_create_lead_no_token(client):
    assert client.post("/leads/", json={
        "company_name": "X", "contact_name": "Y", "email": "y@x.com", "phone": "0",
    }).status_code == 401


def test_get_lead_no_token(client):
    assert client.get(f"/leads/{uuid.uuid4()}").status_code == 401


def test_update_lead_no_token(client):
    assert client.patch(f"/leads/{uuid.uuid4()}", json={"status": "CONTACTED"}).status_code == 401


def test_assign_lead_no_token(client):
    assert client.post(f"/leads/{uuid.uuid4()}/assign",
                       json={"user_id": str(uuid.uuid4())}).status_code == 401


# ── create ─────────────────────────────────────────────────────────────────────

def test_create_lead_success(client, headers):
    resp = client.post("/leads/", json={
        "company_name": "Acme", "contact_name": "Bob",
        "phone": "9000000001", "email": "bob@acme.com",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["company_name"] == "Acme"
    assert data["email"] == "bob@acme.com"
    assert "id" in data


def test_create_lead_missing_company_name(client, headers):
    resp = client.post("/leads/", json={
        "contact_name": "Bob", "email": "bob@acme.com",
    }, headers=headers)
    assert resp.status_code == 422


def test_create_lead_default_status_is_new(client, headers):
    resp = client.post("/leads/", json={
        "company_name": "Corp", "contact_name": "X",
        "email": "x@corp.com", "phone": "1",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "NEW"


# ── get ────────────────────────────────────────────────────────────────────────

def test_get_lead_success(client, headers, seed_lead):
    resp = client.get(f"/leads/{seed_lead['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == seed_lead["id"]


def test_get_lead_not_found(client, headers):
    assert client.get(f"/leads/{uuid.uuid4()}", headers=headers).status_code == 404


def test_get_lead_invalid_uuid(client, headers):
    assert client.get("/leads/not-a-uuid", headers=headers).status_code == 422


# ── list ───────────────────────────────────────────────────────────────────────

def test_list_leads_empty(client, headers):
    resp = client.get("/leads/", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_leads_returns_created(client, headers, seed_lead):
    resp = client.get("/leads/", headers=headers)
    assert resp.status_code == 200
    assert any(l["id"] == seed_lead["id"] for l in resp.json())


def test_list_leads_filter_by_status(client, headers):
    client.post("/leads/", json={
        "company_name": "A", "contact_name": "a", "email": "a@a.com", "phone": "1"
    }, headers=headers)
    resp = client.get("/leads/?status=NEW", headers=headers)
    assert resp.status_code == 200
    for lead in resp.json():
        assert lead["status"] == "NEW"


def test_list_leads_filter_by_assigned_to(client, headers, seed_lead, founder_user):
    client.post(f"/leads/{seed_lead['id']}/assign",
                json={"user_id": str(founder_user.id)}, headers=headers)
    resp = client.get(f"/leads/?assigned_to={founder_user.id}", headers=headers)
    assert resp.status_code == 200
    assert any(l["id"] == seed_lead["id"] for l in resp.json())


# ── update ─────────────────────────────────────────────────────────────────────

def test_update_lead_status(client, headers, seed_lead):
    resp = client.patch(f"/leads/{seed_lead['id']}", json={"status": "CONTACTED"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONTACTED"


def test_update_lead_contact_name(client, headers, seed_lead):
    resp = client.patch(f"/leads/{seed_lead['id']}", json={"contact_name": "Updated"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["contact_name"] == "Updated"


def test_update_lead_not_found(client, headers):
    assert client.patch(f"/leads/{uuid.uuid4()}", json={"status": "CONTACTED"},
                        headers=headers).status_code == 404


# ── assign ─────────────────────────────────────────────────────────────────────

def test_assign_lead_success(client, headers, seed_lead, founder_user):
    resp = client.post(f"/leads/{seed_lead['id']}/assign",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["assigned_to"] == str(founder_user.id)


def test_assign_lead_invalid_user_id(client, headers, seed_lead):
    resp = client.post(f"/leads/{seed_lead['id']}/assign",
                       json={"user_id": "bad-uuid"}, headers=headers)
    assert resp.status_code == 422


def test_assign_lead_not_found(client, headers, founder_user):
    resp = client.post(f"/leads/{uuid.uuid4()}/assign",
                       json={"user_id": str(founder_user.id)}, headers=headers)
    assert resp.status_code == 404


def test_assign_lead_missing_user_id(client, headers, seed_lead):
    resp = client.post(f"/leads/{seed_lead['id']}/assign", json={}, headers=headers)
    assert resp.status_code == 422
