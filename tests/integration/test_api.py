import os
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET", "test-api-secret-key-minimum-32-chars!!")
os.environ.setdefault("DEMO_EMAIL", "admin@finstream.io")
os.environ.setdefault("DEMO_PASSWORD", "testpassword")

from finstream.api.main import app  # noqa: E402
from finstream.api.dependencies import get_jwt_handler  # noqa: E402
from finstream.api.security.jwt_handler import JWTHandler  # noqa: E402

# When DATABASE_URL is absent (local/CI without Docker), patch storage so
# pipeline integration tests run against an in-memory fake instead of PostgreSQL.
if not os.getenv("DATABASE_URL"):
    import finstream.api.routes.pipeline as _pipeline_mod
    from tests.conftest import FakeDataStorage
    _pipeline_mod._make_storage = lambda: FakeDataStorage()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _override_jwt() -> JWTHandler:
    return JWTHandler()


app.dependency_overrides[get_jwt_handler] = _override_jwt

client = TestClient(app, raise_server_exceptions=True)


def get_token(email: str = "admin@finstream.io", password: str = "testpassword") -> str:
    resp = client.post("/auth/token", json={"email": email, "password": password})
    return resp.json()["access_token"]


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class TestAuth:

    def test_valid_credentials_return_token(self) -> None:
        resp = client.post(
            "/auth/token",
            json={"email": "admin@finstream.io", "password": "testpassword"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_invalid_password_returns_401(self) -> None:
        resp = client.post(
            "/auth/token",
            json={"email": "admin@finstream.io", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_unknown_email_returns_401(self) -> None:
        resp = client.post(
            "/auth/token",
            json={"email": "hacker@evil.com", "password": "testpassword"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:

    def test_health_returns_200(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_ready_returns_200(self) -> None:
        resp = client.get("/ready")
        assert resp.status_code == 200

    def test_metrics_returns_prometheus_text(self) -> None:
        resp = client.get("/metrics")
        assert resp.status_code == 200
        assert "finstream" in resp.text or "python" in resp.text

    def test_health_requires_no_auth(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class TestPipeline:

    def test_run_pipeline_requires_auth(self) -> None:
        resp = client.post(
            "/pipeline/run",
            json={"business_date": "2024-01-15"},
        )
        assert resp.status_code in (401, 403)

    def test_run_pipeline_with_invalid_token_returns_401(self) -> None:
        resp = client.post(
            "/pipeline/run",
            json={"business_date": "2024-01-15"},
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert resp.status_code == 401

    def test_run_pipeline_returns_202(self) -> None:
        resp = client.post(
            "/pipeline/run",
            json={"business_date": "2024-01-15"},
            headers=auth_headers(),
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "run_id" in body
        assert body["status"] == "COMPLETED"
        assert body["total_records"] > 0

    def test_run_pipeline_response_has_quality_score(self) -> None:
        resp = client.post(
            "/pipeline/run",
            json={"business_date": "2024-01-15"},
            headers=auth_headers(),
        )
        assert resp.status_code == 202
        assert resp.json()["quality_score"] == 100.0

    def test_get_pipeline_status_after_run(self) -> None:
        run_resp = client.post(
            "/pipeline/run",
            json={"business_date": "2024-01-15"},
            headers=auth_headers(),
        )
        run_id = run_resp.json()["run_id"]
        status_resp = client.get(
            f"/pipeline/status/{run_id}",
            headers=auth_headers(),
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["run_id"] == run_id

    def test_get_unknown_run_returns_404(self) -> None:
        resp = client.get(
            "/pipeline/status/nonexistent-run-id",
            headers=auth_headers(),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------

class TestQuality:

    def test_list_reports_requires_auth(self) -> None:
        resp = client.get("/quality/reports")
        assert resp.status_code in (401, 403)

    def test_list_reports_returns_list(self) -> None:
        resp = client.get("/quality/reports", headers=auth_headers())
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_unknown_report_returns_404(self) -> None:
        resp = client.get(
            "/quality/reports/nonexistent-run",
            headers=auth_headers(),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboard:

    def test_dashboard_is_publicly_accessible(self) -> None:
        resp = client.get("/dashboard")
        assert resp.status_code == 200

    def test_dashboard_returns_html(self) -> None:
        resp = client.get("/dashboard", headers=auth_headers())
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "<html" in resp.text

    def test_dashboard_contains_chart_js(self) -> None:
        resp = client.get("/dashboard", headers=auth_headers())
        assert "chart.js" in resp.text.lower()
