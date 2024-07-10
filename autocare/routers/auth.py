from functools import wraps
from http import HTTPStatus
from typing import Annotated, Callable

from conf.settings import settings
from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from schemas import Message, Token
from security import (
    auth_google,
    confirm_token,
    create_access_token,
    get_password_hash,
    verify_password,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]


def handle_google_auth(func: Callable):
    @wraps(func)
    def wrapper(data, session):
        if isinstance(data, str):
            data = auth_google(data)
        return func(data, session)

    return wrapper


@router.post("/token", response_model=Token)
@handle_google_auth
def login_for_access_token(data: OAuth2Form, session: Session):
    user = session.scalar(select(User).where(User.email == data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Email not confirmed",
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}", response_model=Message)
def confirm_email(token: str, session: Session):
    email = confirm_token(token)

    if not email:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid or expired token")

    db_user = session.scalar(select(User).where(User.email == email))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    db_user.is_active = True
    session.commit()

    return {"message": "Account confirmed"}


@router.get("/new-password/{token}", response_model=Message)
def new_password(token: str, password: str, session: Session):
    email = confirm_token(token)

    if not email:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid or expired token")

    db_user = session.scalar(select(User).where(User.email == email))

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    db_user.password = get_password_hash(password)
    session.commit()

    return {"message": "Password updated"}


@router.get("/google/token", response_model=Message)
def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"  # noqa
    }
