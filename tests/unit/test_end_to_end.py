# tests/test_end_to_end.py

import uuid
import pytest
from tests.conftest import _seed_user, get_token, auth


def test_full_project_lifecycle(client, db):
    # ── seed user + login ─────────────────────────────────────────────────────
    user = _seed_user(db, "poc@kerna.in", "pass123")
    token = get_token(client, "poc@kerna.in", "pass123")
    h = auth(token)
    uid = str(user.id)

    # ── create lead ───────────────────────────────────────────────────────────
    r = client.post("/leads/", json={
        "company_name": "Kerna Client Ltd",
        "contact_name": "Ravi",
        "phone": "9876543210",
        "email": "ravi@kernaclient.com",
    }, headers=h)
    assert r.status_code == 200, r.text
    lead = r.json()
    assert lead["status"] == "NEW"
    lead_id = lead["id"]

    # ── update lead ───────────────────────────────────────────────────────────
    r = client.patch(f"/leads/{lead_id}", json={"status": "CONTACTED"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "CONTACTED"

    # ── assign lead ───────────────────────────────────────────────────────────
    r = client.post(f"/leads/{lead_id}/assign", json={"user_id": uid}, headers=h)
    assert r.status_code == 200
    assert r.json()["assigned_to"] == uid

    # ── create quotation ──────────────────────────────────────────────────────
    r = client.post("/quotations/", json={
        "lead_id": lead_id,
        "poc_id": uid,
        "template_type": "WEB",
    }, headers=h)
    assert r.status_code == 200, r.text
    q_id = r.json()["id"]
    assert r.json()["status"] == "DRAFT"

    # ── add version ───────────────────────────────────────────────────────────
    r = client.post(f"/quotations/{q_id}/versions", json={
        "subtotal": "80000", "discount": "5000", "total": "75000",
    }, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["version_number"] == 1
    v_id = r.json()["id"]

    # ── add line items ────────────────────────────────────────────────────────
    r = client.post(f"/quotations/versions/{v_id}/line-items", json={
        "items": [
            {"title": "UI Design", "unit_price": "30000", "quantity": 1},
            {"title": "Development", "unit_price": "40000", "quantity": 1},
            {"title": "SEO", "unit_price": "5000", "quantity": 1},
        ]
    }, headers=h)
    assert r.status_code == 200, r.text
    assert len(r.json()) == 3

    # ── mark final ────────────────────────────────────────────────────────────
    r = client.post(f"/quotations/versions/{v_id}/final", headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["is_final"] is True

    # ── accept → project created ──────────────────────────────────────────────
    r = client.post(f"/quotations/{q_id}/accept", headers=h)
    assert r.status_code == 200, r.text
    accept = r.json()
    assert accept["quotation"]["status"] == "ACCEPTED"
    project = accept["project"]
    assert project["status"] == "INITIATED"
    p_id = project["id"]

    # ── create module ─────────────────────────────────────────────────────────
    r = client.post(f"/projects/{p_id}/modules", json={"module_type": "DEV"}, headers=h)
    assert r.status_code == 200, r.text
    m_id = r.json()["id"]
    assert r.json()["project_id"] == p_id

    # ── assign user to module ─────────────────────────────────────────────────
    r = client.post(f"/modules/{m_id}/assign", json={"user_id": uid}, headers=h)
    assert r.status_code == 200, r.text

    # verify
    r = client.get(f"/modules/{m_id}/assignments", headers=h)
    assert r.status_code == 200
    assert any(a["user_id"] == uid for a in r.json())

    # ── upload module version ─────────────────────────────────────────────────
    r = client.post(f"/modules/{m_id}/versions", json={
        "file_url": "https://cdn.kerna.in/dev-v1.zip",
        "notes": "Initial build",
    }, headers=h)
    assert r.status_code == 200, r.text
    mv_id = r.json()["id"]

    # ── request approval ──────────────────────────────────────────────────────
    r = client.post(f"/approvals/versions/{mv_id}/request", headers=h)
    assert r.status_code == 200, r.text
    approval = r.json()
    assert approval["status"] == "PENDING"
    assert approval["lock_expires_at"] is not None
    appr_id = approval["id"]

    # ── approve ───────────────────────────────────────────────────────────────
    r = client.post(f"/approvals/{appr_id}/approve", json={"user_id": uid}, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "APPROVED"
    assert r.json()["approved_by"] == uid

    # ── consistency checks ────────────────────────────────────────────────────
    assert client.get(f"/leads/{lead_id}", headers=h).json()["status"] == "CONTACTED"
    assert client.get(f"/quotations/{q_id}", headers=h).json()["status"] == "ACCEPTED"
    modules = client.get(f"/projects/{p_id}/modules", headers=h).json()
    assert any(m["id"] == m_id for m in modules)

    # ── duplicate approval blocked ────────────────────────────────────────────
    r = client.post(f"/approvals/versions/{mv_id}/request", headers=h)
    assert r.status_code == 422


def test_unauthenticated_cannot_touch_anything(client):
    """Every endpoint must reject no-token requests."""
    fake = str(uuid.uuid4())
    checks = [
        ("GET",   f"/leads/",                      None),
        ("POST",  f"/leads/",                      {"company_name": "X"}),
        ("GET",   f"/leads/{fake}",                None),
        ("PATCH", f"/leads/{fake}",                {"status": "X"}),
        ("POST",  f"/leads/{fake}/assign",         {"user_id": fake}),
        ("POST",  f"/quotations/",                 {"lead_id": fake}),
        ("GET",   f"/quotations/{fake}",           None),
        ("POST",  f"/quotations/{fake}/versions",  {}),
        ("POST",  f"/quotations/{fake}/accept",    None),
        ("POST",  f"/projects/{fake}/modules",     {"module_type": "DEV"}),
        ("GET",   f"/projects/{fake}/modules",     None),
        ("POST",  f"/approvals/versions/{fake}/request", None),
        ("POST",  f"/approvals/{fake}/approve",    {"user_id": fake}),
        ("POST",  f"/approvals/{fake}/reject",     {"user_id": fake}),
        ("POST",  f"/approvals/{fake}/withdraw",   {"user_id": fake}),
    ]
    for method, url, body in checks:
        if method == "GET":
            resp = client.get(url)
        elif method == "POST":
            resp = client.post(url, json=body or {})
        elif method == "PATCH":
            resp = client.patch(url, json=body or {})
        assert resp.status_code == 401, f"{method} {url} → expected 401 got {resp.status_code}"


def test_accept_without_final_blocks_flow(client, db):
    user = _seed_user(db, "poc2@kerna.in", "pass")
    h = auth(get_token(client, "poc2@kerna.in", "pass"))

    lead = client.post("/leads/", json={
        "company_name": "Block Corp", "contact_name": "Dev",
        "email": "dev@block.com", "phone": "1",
    }, headers=h).json()
    q = client.post("/quotations/", json={
        "lead_id": lead["id"], "poc_id": str(user.id), "template_type": "BRANDING",
    }, headers=h).json()
    v = client.post(f"/quotations/{q['id']}/versions",
                    json={"subtotal": "5000", "total": "5000"}, headers=h).json()
    client.post(f"/quotations/versions/{v['id']}/line-items", json={
        "items": [{"title": "Logo", "unit_price": "5000", "quantity": 1}]
    }, headers=h)
    # deliberately NOT marking final
    r = client.post(f"/quotations/{q['id']}/accept", headers=h)
    assert r.status_code == 422


def test_reject_then_new_version_new_approval(client, db):
    """After rejection, upload new version and request fresh approval."""
    user = _seed_user(db, "dev@kerna.in", "devpass")
    h = auth(get_token(client, "dev@kerna.in", "devpass"))
    uid = str(user.id)

    lead = client.post("/leads/", json={
        "company_name": "Cycle Corp", "contact_name": "C",
        "email": "c@cycle.com", "phone": "2",
    }, headers=h).json()
    q = client.post("/quotations/", json={
        "lead_id": lead["id"], "poc_id": uid, "template_type": "WEB",
    }, headers=h).json()
    v = client.post(f"/quotations/{q['id']}/versions",
                    json={"subtotal": "1000", "total": "1000"}, headers=h).json()
    client.post(f"/quotations/versions/{v['id']}/line-items", json={
        "items": [{"title": "X", "unit_price": "1000", "quantity": 1}]
    }, headers=h)
    client.post(f"/quotations/versions/{v['id']}/final", headers=h)
    proj = client.post(f"/quotations/{q['id']}/accept", headers=h).json()["project"]

    mod = client.post(f"/projects/{proj['id']}/modules",
                      json={"module_type": "DESIGN"}, headers=h).json()
    m_id = mod["id"]

    # v1 upload + reject
    mv1 = client.post(f"/modules/{m_id}/versions", json={
        "file_url": "https://cdn.kerna.in/v1.zip", "notes": "v1"
    }, headers=h).json()["id"]
    a1 = client.post(f"/approvals/versions/{mv1}/request", headers=h).json()
    client.post(f"/approvals/{a1['id']}/reject", json={"user_id": uid}, headers=h)

    # v2 upload + approve
    mv2 = client.post(f"/modules/{m_id}/versions", json={
        "file_url": "https://cdn.kerna.in/v2.zip", "notes": "v2 revised"
    }, headers=h).json()["id"]
    a2 = client.post(f"/approvals/versions/{mv2}/request", headers=h).json()
    assert a2["id"] != a1["id"]
    r = client.post(f"/approvals/{a2['id']}/approve", json={"user_id": uid}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "APPROVED"
