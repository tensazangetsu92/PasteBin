import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from microservices.pastebin_backend.app.schemas import PostCreate
from microservices.pastebin_backend.app.services import add_post_service


@pytest.mark.asyncio
async def test_add_post_service():
    # Мокаем зависимости
    mock_db = AsyncMock(spec=AsyncSession)  # Мок базы данных
    mock_get_hash = AsyncMock(return_value="mocked_hash")  # Мок генерации хэша
    mock_get_record_by_short_key = AsyncMock(return_value=None)  # Проверка уникальности хэша
    mock_upload_file_to_bucket = AsyncMock(return_value="mocked_blob_url")  # Мок загрузки файла
    mock_create_record = AsyncMock(return_value={"id": 1, "name": "Test Post"})  # Мок создания записи

    text_data = PostCreate(
        name="Test Post",
        text="Test content",
        expires_at="2040-12-30T14:01:49"
    )

    current_user_id = 123

    with patch("microservices.pastebin_backend.app.services.get_hash", mock_get_hash), \
         patch("microservices.pastebin_backend.app.services.get_record_by_short_key", mock_get_record_by_short_key), \
         patch("microservices.pastebin_backend.app.services.upload_file_to_bucket", mock_upload_file_to_bucket), \
         patch("microservices.pastebin_backend.app.services.create_record", mock_create_record):

        result = await add_post_service(text_data, mock_db, current_user_id)

        assert result["id"] == 1
        assert result["name"] == "Test Post"

    # Проверяем, что нужные функции вызывались
    mock_get_hash.assert_called()
    mock_get_record_by_short_key.assert_called()
    mock_upload_file_to_bucket.assert_called()
    mock_create_record.assert_called()
    mock_db.commit.assert_called()


