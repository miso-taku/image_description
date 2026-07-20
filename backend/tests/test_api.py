"""API-level tests. The description service is stubbed (no OpenAI calls)."""

from __future__ import annotations

from app.core.errors import (
    ConfigurationError,
    UpstreamRateLimitedError,
    UpstreamTimeoutError,
)
from app.schemas.description import ImageDescription
from tests.conftest import PNG_BYTES, FakeDescriptionService


def test_health_ok(make_client) -> None:
    client = make_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["openai_configured"] is True


def test_create_description_success(make_client) -> None:
    service = FakeDescriptionService(output=ImageDescription(description="犬が芝生の上にいます。"))
    client = make_client(service)
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("dog.png", PNG_BYTES, "image/png")},
        data={"detail": "standard"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["description"] == "犬が芝生の上にいます。"
    assert body["detail"] == "standard"
    assert body["model"] == "gpt-4.1-mini"
    assert body["request_id"]
    assert resp.headers.get("X-Request-ID")
    assert service.received[0][1].value == "standard"


def test_invalid_detail_rejected(make_client) -> None:
    client = make_client()
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("dog.png", PNG_BYTES, "image/png")},
        data={"detail": "verbose"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "invalid_detail"


def test_unsupported_type_rejected(make_client) -> None:
    client = make_client()
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("note.txt", b"just some text, not an image", "text/plain")},
        data={"detail": "brief"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "invalid_image_type"


def test_empty_image_rejected(make_client) -> None:
    client = make_client()
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("empty.png", b"", "image/png")},
        data={"detail": "brief"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "empty_image"


def test_configuration_error_mapped(make_client) -> None:
    service = FakeDescriptionService(exc=ConfigurationError())
    client = make_client(service)
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("dog.png", PNG_BYTES, "image/png")},
        data={"detail": "brief"},
    )
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "configuration_error"


def test_upstream_rate_limit_mapped(make_client) -> None:
    service = FakeDescriptionService(exc=UpstreamRateLimitedError())
    client = make_client(service)
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("dog.png", PNG_BYTES, "image/png")},
        data={"detail": "brief"},
    )
    assert resp.status_code == 429
    assert resp.json()["error"]["code"] == "rate_limited"


def test_upstream_timeout_mapped(make_client) -> None:
    service = FakeDescriptionService(exc=UpstreamTimeoutError())
    client = make_client(service)
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("dog.png", PNG_BYTES, "image/png")},
        data={"detail": "detailed"},
    )
    assert resp.status_code == 504
    assert resp.json()["error"]["code"] == "upstream_timeout"


def test_error_response_has_no_internal_details(make_client) -> None:
    service = FakeDescriptionService(exc=RuntimeError("secret internal detail"))
    client = make_client(service)
    resp = client.post(
        "/api/v1/descriptions",
        files={"image": ("dog.png", PNG_BYTES, "image/png")},
        data={"detail": "brief"},
    )
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "internal_error"
    assert "secret internal detail" not in body["error"]["message"]
