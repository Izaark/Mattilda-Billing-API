from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    print(f"API Key: {api_key}")
    print(f"Settings API Key: {settings.API_KEY}")
    print(f"API Key length: {len(api_key)}")
    print(f"Settings API Key length: {len(settings.API_KEY)}")
    print(f"API Key equals Settings API Key: {api_key == settings.API_KEY}")
    print(f"API Key type: {type(api_key)}")
    print(f"Settings API Key type: {type(settings.API_KEY)}")
    print(f"API Key is equal to Settings API Key: {api_key == settings.API_KEY}")
    print(f"API Key is not equal to Settings API Key: {api_key != settings.API_KEY}")
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key

