from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import get_token_subject
from app.core.logging import get_logger
from app.models.user import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")
logger = get_logger(__name__)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user_id = get_token_subject(token)
    if not user_id:
        logger.warning("Authentication failed: invalid token subject")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    try:
        parsed_user_id = UUID(user_id)
    except ValueError as exc:
        logger.warning("Authentication failed: malformed user id in token subject")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials") from exc

    user = await User.get_or_none(id=parsed_user_id)
    if user is None:
        logger.warning("Authentication failed: user not found for id=%s", parsed_user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
