import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_backend.app.main import app
from microservices.pastebin_backend.app.postgresql_db.database import get_async_session
from microservices.pastebin_backend.app.user_management.token_utils import get_current_user_id
from microservices.pastebin_backend.app.services import get_hash, get_record_by_short_key, upload_file_to_bucket, create_record

client = TestClient(app)

# Фикстуры
@pytest.fixture
def override_get_current_user_id():
    return 123  # Подставляем тестовое значение

@pytest.fixture
def override_get_db():
    return AsyncMock(spec=AsyncSession)  # Мок базы данных

@pytest.fixture
def mock_redis():
    # Мокируем объект redis_cache
    mock_redis = AsyncMock()
    return mock_redis

@pytest.fixture
def mock_services():
    """Мокируем все внешние сервисы"""
    with patch("microservices.pastebin_backend.app.services.get_hash", AsyncMock(return_value="mocked_hash")) as mock_get_hash, \
         patch("microservices.pastebin_backend.app.services.get_record_by_short_key", AsyncMock(return_value=None)) as mock_get_record_by_short_key, \
         patch("microservices.pastebin_backend.app.services.upload_file_to_bucket", AsyncMock(return_value="mocked_blob_url")) as mock_upload_file_to_bucket, \
         patch("microservices.pastebin_backend.app.services.create_record", AsyncMock(return_value={"id": 1, "name": "Test Post"})) as mock_create_record, \
         patch("microservices.pastebin_backend.app.services.get_file_from_bucket", AsyncMock(return_value={"content": "File content", "size": 1024})) as mock_get_file_from_bucket, \
         patch("microservices.pastebin_backend.app.services.increment_views_in_cache", AsyncMock(return_value=10)) as mock_increment_views_in_cache, \
         patch("microservices.pastebin_backend.app.services.create_post_cache", AsyncMock(return_value=None)) as mock_create_post_cache:
        yield mock_get_hash, mock_get_record_by_short_key, mock_upload_file_to_bucket, mock_create_record, \
               mock_get_file_from_bucket, mock_increment_views_in_cache, mock_create_post_cache


def test_add_post(override_get_current_user_id, override_get_db, mock_services):
    app.dependency_overrides[get_current_user_id] = lambda: override_get_current_user_id
    app.dependency_overrides[get_async_session] = lambda: override_get_db  # Если база используется
    text_data = {
        "name": "Test Post",
        "text": "Test content",
        "expires_at": "2040-12-30T14:01:49"
    }
    response = client.post("/api/add-post", json=text_data)
    assert response.status_code == 200
    app.dependency_overrides.clear()  # Очищаем зависимости после теста


def test_get_popular_posts(mock_redis):
    mock_redis.get.return_value = json.dumps([{
        "id": 23,
        "name": "Post 1",
        "created_at": "2025-02-01T12:00:00",
        "text_size_kilobytes": 1.23,
        "short_key": "mocked_key",
        "expires_at": "2040-12-30T14:01:49"
    }])

    app.state.redis = mock_redis
    response = client.get("/api/get-popular-posts")
    mock_redis.get.assert_called_once_with("most_popular_posts")

    assert response.status_code == 200
    assert "posts" in response.json()
    assert len(response.json()["posts"]) > 0  # Убедитесь, что посты присутствуют
    assert response.json()["posts"][0]["name"] == "Post 1"
    assert "text_size_kilobytes" in response.json()["posts"][0]
    assert "short_key" in response.json()["posts"][0]
    assert "expires_at" in response.json()["posts"][0]
    mock_redis.get.reset_mock(return_value=True)



def test_get_post(mock_redis, mock_services, override_get_current_user_id, override_get_db):
    app.dependency_overrides[get_current_user_id] = lambda: override_get_current_user_id
    app.dependency_overrides[get_async_session] = lambda: override_get_db  # Если база используется
    short_key = "mocked_key"
    mock_redis.get.return_value = json.dumps({
        "id": 1,
        "name": "aaaaaaaaaaaa",
        "text": "aaaaaaaaaaaaaaaaaaaaaa",
        "text_size_kilobytes": 0.02,
        "short_key": "BRpDIcrp",
        "created_at": "2025-02-13T17:25:15.405543",
        "expires_at": "2040-12-30T14:01:49.746000",
        "views": 1
    })
    app.state.redis = mock_redis
    response = client.get(f"/api/get-post/{short_key}")
    assert response.json() == {
        "id": 1,
        "name": "aaaaaaaaaaaa",
        "text": "aaaaaaaaaaaaaaaaaaaaaa",
        "text_size_kilobytes": 0.02,
        "short_key": "BRpDIcrp",
        "created_at": "2025-02-13T17:25:15.405543",
        "expires_at": "2040-12-30T14:01:49.746000",
        "views": 2
    }

    assert response.status_code == 200

    mock_redis.get.reset_mock(return_value=True)
    app.dependency_overrides.clear()
