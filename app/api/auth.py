from fastapi import APIRouter, HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserRead
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


def normalize_email(email: str) -> str:
    return email.strip().lower()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate) -> TokenResponse:
    body.email = normalize_email(body.email)
    logger.info("Registration attempt email=%s", body.email)
    if await User.filter(email=body.email).exists():
        logger.warning("Registration blocked: email already registered email=%s", body.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await User.create(email=body.email, hashed_password=hash_password(body.password))
    token = create_access_token(subject=str(user.id))
    logger.info("User registered: %s", user.email)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    body.email = normalize_email(body.email)
    user = await User.get_or_none(email=body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=str(user.id))
    logger.info("User logged in: %s", user.email)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/login/form")
async def login_form(form: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(email=form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}