from http import HTTPStatus
import secrets
from typing import Annotated

from conf.settings import settings
from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from routers.users import create_user
from schemas import Message, Token, UserSchema
from security import (
    confirm_token,
    create_access_token,
    get_password_hash,
    verify_password,
)
from sqlalchemy import select
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter(prefix="/auth", tags=["auth"])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]


@router.post("/token", response_model=Token)
def login_for_access_token(data: OAuth2Form, session: Session):
    user = ""

    if data.username == "google_user":
        try:
            id_info = id_token.verify_oauth2_token(
                data.password, requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer")

            user_email = id_info["email"]
            user = session.scalar(select(User).where(User.email == user_email))

            if not user:
                user = UserSchema(
                    email=id_info.get("email"),
                    first_name=id_info.get("given_name"),
                    last_name=id_info.get("family_name"),
                    username=id_info.get("email").split("@")[0],
                    phone_number=id_info.get("phone_number", "Não disponível"),
                    password=get_password_hash(secrets.token_urlsafe(16)),
                )
                user = create_user(user, session)
                db_user = session.scalar(select(User).where(User.email == user.email))
                db_user.is_active = True
                session.commit()
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid Google token",
            )
    else:
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
