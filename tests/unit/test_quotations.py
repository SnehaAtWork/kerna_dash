# tests/test_quotations.py

import uuid
import pytest
from tests.conftest import auth


# ── 401 guards ─────────────────────────────────────────────────────────────────

def test_create_quotation_no_token(client):
    assert client.post("/quotations/", json={"lead_id": str(uuid.uuid4())}).status_code == 401


def test_get_quotation_no_token(client):
    assert client.get(f"/quotations/{uuid.uuid4()}").status_code == 401


def test_add_version_no_token(client):
    assert client.post(f"/quotations/{uuid.uuid4()}/versions", json={}).status_code == 401


def test_accept_no_token(client):
    assert client.post(f"/quotations/{uuid.uuid4()}/accept").status_code == 401


# ── create ─────────────────────────────────────────────────────────────────────

def test_create_quotation_success(client, headers, seed_lead):
    resp = client.post("/quotations/", json={
        "lead_id": seed_lead["id"],
        "poc_id": str(uuid.uuid4()),
        "template_type": "WEB",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lead_id"] == seed_lead["id"]
    assert data["status"] == "DRAFT"


def test_create_quotation_invalid_lead_id(client, headers):
    resp = client.post("/quotations/", json={
        "lead_id": "not-a-uuid", "poc_id": str(uuid.uuid4()),
    }, headers=headers)
    assert resp.status_code == 422


def test_create_quotation_missing_lead_id(client, headers):
    resp = client.post("/quotations/", json={"poc_id": str(uuid.uuid4())}, headers=headers)
    assert resp.status_code == 422


# ── get ────────────────────────────────────────────────────────────────────────

def test_get_quotation_success(client, headers, seed_quotation):
    resp = client.get(f"/quotations/{seed_quotation['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == seed_quotation["id"]


def test_get_quotation_not_found(client, headers):
    assert client.get(f"/quotations/{uuid.uuid4()}", headers=headers).status_code == 404


# ── versions ───────────────────────────────────────────────────────────────────

def test_add_version_success(client, headers, seed_quotation):
    resp = client.post(f"/quotations/{seed_quotation['id']}/versions", json={
        "subtotal": "5000", "discount": "500", "total": "4500",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["version_number"] == 1
    assert data["is_final"] is False


def test_versions_increment(client, headers, seed_quotation):
    q_id = seed_quotation["id"]
    r1 = client.post(f"/quotations/{q_id}/versions",
                     json={"subtotal": "1000", "total": "1000"}, headers=headers)
    r2 = client.post(f"/quotations/{q_id}/versions",
                     json={"subtotal": "2000", "total": "2000"}, headers=headers)
    assert r1.json()["version_number"] == 1
    assert r2.json()["version_number"] == 2


def test_add_version_quotation_not_found(client, headers):
    resp = client.post(f"/quotations/{uuid.uuid4()}/versions",
                       json={"subtotal": "1000", "total": "1000"}, headers=headers)
    assert resp.status_code == 404


def test_list_versions(client, headers, seed_quotation):
    q_id = seed_quotation["id"]
    client.post(f"/quotations/{q_id}/versions",
                json={"subtotal": "1000", "total": "1000"}, headers=headers)
    resp = client.get(f"/quotations/{q_id}/versions", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_versions_no_token(client, seed_quotation):
    assert client.get(f"/quotations/{seed_quotation['id']}/versions").status_code == 401


# ── line items ─────────────────────────────────────────────────────────────────

def _add_version(client, headers, q_id):
    r = client.post(f"/quotations/{q_id}/versions",
                    json={"subtotal": "5000", "total": "5000"}, headers=headers)
    assert r.status_code == 200
    return r.json()["id"]


def test_add_line_items_success(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/line-items", json={
        "items": [{"title": "Design", "unit_price": "2500", "quantity": 2}]
    }, headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_add_multiple_line_items(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/line-items", json={
        "items": [
            {"title": "A", "unit_price": "100", "quantity": 1},
            {"title": "B", "unit_price": "200", "quantity": 3},
        ]
    }, headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_empty_line_items_fails(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/line-items",
                       json={"items": []}, headers=headers)
    assert resp.status_code == 422


def test_line_items_not_list_fails(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/line-items",
                       json={"items": "wrong"}, headers=headers)
    assert resp.status_code == 422


def test_line_item_zero_quantity_fails(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/line-items", json={
        "items": [{"title": "X", "unit_price": "100", "quantity": 0}]
    }, headers=headers)
    assert resp.status_code == 422


def test_line_item_missing_price_fails(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/line-items", json={
        "items": [{"title": "X", "quantity": 1}]
    }, headers=headers)
    assert resp.status_code == 422


def test_line_items_version_not_found(client, headers):
    resp = client.post(f"/quotations/versions/{uuid.uuid4()}/line-items", json={
        "items": [{"title": "X", "unit_price": "100", "quantity": 1}]
    }, headers=headers)
    assert resp.status_code == 404


def test_line_items_no_token(client, seed_quotation):
    assert client.post(f"/quotations/versions/{uuid.uuid4()}/line-items",
                       json={"items": []}).status_code == 401


# ── mark final ─────────────────────────────────────────────────────────────────

def test_mark_final_success(client, headers, seed_quotation):
    v_id = _add_version(client, headers, seed_quotation["id"])
    resp = client.post(f"/quotations/versions/{v_id}/final", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_final"] is True


def test_mark_final_replaces_previous(client, headers, seed_quotation):
    q_id = seed_quotation["id"]
    v1 = _add_version(client, headers, q_id)
    v2 = _add_version(client, headers, q_id)
    client.post(f"/quotations/versions/{v1}/final", headers=headers)
    client.post(f"/quotations/versions/{v2}/final", headers=headers)
    versions = {v["id"]: v for v in client.get(
        f"/quotations/{q_id}/versions", headers=headers).json()}
    assert versions[v2]["is_final"] is True
    assert versions[v1]["is_final"] is False


def test_mark_final_not_found(client, headers):
    assert client.post(f"/quotations/versions/{uuid.uuid4()}/final",
                       headers=headers).status_code == 404


def test_mark_final_no_token(client):
    assert client.post(f"/quotations/versions/{uuid.uuid4()}/final").status_code == 401


# ── accept ─────────────────────────────────────────────────────────────────────

def test_accept_success(client, headers, seed_final_quotation):
    q_id = seed_final_quotation["quotation"]["id"]
    resp = client.post(f"/quotations/{q_id}/accept", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["quotation"]["status"] == "ACCEPTED"
    assert data["project"] is not None
    assert data["project"]["status"] == "INITIATED"


def test_accept_without_final_fails(client, headers, seed_quotation):
    q_id = seed_quotation["id"]
    _add_version(client, headers, q_id)  # version exists but not final
    resp = client.post(f"/quotations/{q_id}/accept", headers=headers)
    assert resp.status_code == 422


def test_accept_idempotent(client, headers, seed_final_quotation):
    q_id = seed_final_quotation["quotation"]["id"]
    r1 = client.post(f"/quotations/{q_id}/accept", headers=headers)
    r2 = client.post(f"/quotations/{q_id}/accept", headers=headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["project"]["id"] == r2.json()["project"]["id"]


def test_accept_not_found(client, headers):
    assert client.post(f"/quotations/{uuid.uuid4()}/accept", headers=headers).status_code == 404
