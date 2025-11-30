from fastapi import Header, HTTPException, status
from typing import Optional

SECRET_KEY = "devacia_wolf_2025"

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
