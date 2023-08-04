import base64
import secrets

import pytest
from httpx import AsyncClient

from secrets_app.routes.secret import get_hash

from .data_for_tests import secret_generate_data, secret_phrases

pytestmark = pytest.mark.anyio


async def test_ok(test_app: AsyncClient):
    response = await test_app.get("/health")
    assert response.status_code == 200


@pytest.mark.parametrize("secret_phrase", secret_phrases)
async def test_get_hash(secret_phrase: str):
    secret_key = secrets.token_urlsafe(32)
    key = base64.urlsafe_b64decode(get_hash(secret_key, secret_phrase))
    assert len(key) == 32


@pytest.mark.parametrize("secret_phrase, secret", secret_generate_data)
async def test_generate_and_get(test_app: AsyncClient, secret_phrase: str, secret: str):
    generate_key = await test_app.post(
        "/generate",
        json={"secret_phrase": secret_phrase, "secret": secret},
    )
    assert generate_key.status_code == 201
    secret_key = generate_key.json()["key"]
    get_key = await test_app.get(f"/secret/{secret_key}?secret_phrase={secret_phrase}")
    assert get_key.status_code == 200
    assert get_key.json()["secret"] == secret
