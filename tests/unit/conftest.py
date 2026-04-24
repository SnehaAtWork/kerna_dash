# tests/conftest.py

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_TEST_URL = "sqlite:///./test_temp.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.main import app
from app.core.dependencies import get_db
from app.db.base import Base
from app.modules.users.models import User
from app.core.security import hash_password  # NEW

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


def _seed_user(db, email: str, password: str) -> User:
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email=email,
        password_hash=hash_password(password),  # HASHED NOW
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_token(client, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"login failed: {resp.text}"
    return resp.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def founder_user(db):
    return _seed_user(db, "founder@kerna.in", "secret123")


@pytest.fixture
def founder_token(client, founder_user):
    return get_token(client, founder_user.email, "secret123")


@pytest.fixture
def headers(founder_token):
    return auth(founder_token)


@pytest.fixture
def seed_lead(client, headers):
    r = client.post("/leads/", json={
        "company_name": "Test Corp",
        "contact_name": "Alice",
        "phone": "9999999999",
        "email": "alice@testcorp.com",
    }, headers=headers)
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def seed_quotation(client, headers, seed_lead):
    r = client.post("/quotations/", json={
        "lead_id": seed_lead["id"],
        "poc_id": str(uuid.uuid4()),
        "template_type": "WEB",
    }, headers=headers)
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def seed_final_quotation(client, headers, seed_quotation):
    q_id = seed_quotation["id"]
    ver = client.post(f"/quotations/{q_id}/versions", json={
        "subtotal": "10000", "discount": "0", "total": "10000",
    }, headers=headers)
    assert ver.status_code == 200
    v_id = ver.json()["id"]
    client.post(f"/quotations/versions/{v_id}/line-items", json={
        "items": [{"title": "Web Dev", "unit_price": "5000", "quantity": 2}]
    }, headers=headers)
    client.post(f"/quotations/versions/{v_id}/final", headers=headers)
    return {"quotation": seed_quotation, "version_id": v_id}


@pytest.fixture
def seed_project(client, headers, seed_final_quotation):
    q_id = seed_final_quotation["quotation"]["id"]
    r = client.post(f"/quotations/{q_id}/accept", headers=headers)
    assert r.status_code == 200
    return r.json()["project"]


@pytest.fixture
def seed_module(client, headers, seed_project):
    r = client.post(f"/projects/{seed_project['id']}/modules", json={
        "module_type": "DEV",
    }, headers=headers)
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def seed_module_version(client, headers, seed_module):
    r = client.post(f"/modules/{seed_module['id']}/versions", json={
        "file_url": "https://cdn.kerna.in/file.zip",
        "notes": "v1",
    }, headers=headers)
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def seed_approval(client, headers, seed_module_version):
    r = client.post(f"/approvals/versions/{seed_module_version['id']}/request",
                    headers=headers)
    assert r.status_code == 200
    return r.json()