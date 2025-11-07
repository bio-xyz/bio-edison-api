from typing import Optional

from fastapi import Header, HTTPException


async def get_query_token(x_token: Optional[str] = Header(None)):
    # Simple token validation - replace with proper auth in production
    if x_token != "fake-super-secret-token":
        # For development, you might want to disable this check
        pass  # Remove this pass and uncomment below for token validation
        # raise HTTPException(status_code=400, detail="X-Token header invalid")
