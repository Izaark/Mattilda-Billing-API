import pytest
from fastapi import HTTPException

from app.infrastructure.auth import verify_api_key


class TestAPIKeyAuth:
    def test_verify_api_key_with_valid_key(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-secret-key")
        from app.config import settings
        settings.API_KEY = "test-secret-key"
        
        result = verify_api_key("test-secret-key")
        
        assert result == "test-secret-key"

    def test_verify_api_key_with_invalid_key(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-secret-key")
        from app.config import settings
        settings.API_KEY = "test-secret-key"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key("wrong-key")
        
        assert exc_info.value.status_code == 403
        assert "Invalid API Key" in exc_info.value.detail

    def test_verify_api_key_with_missing_key(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-secret-key")
        from app.config import settings
        settings.API_KEY = "test-secret-key"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(None)
        
        assert exc_info.value.status_code == 401
        assert "Missing API Key" in exc_info.value.detail

