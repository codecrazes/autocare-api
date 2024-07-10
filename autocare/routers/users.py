import secrets
import sys
from http import HTTPStatus
from typing import Annotated

from routers.auth import login_google
from conf.settings import settings
from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import User
from schemas import Message, UserList, UserPublic, UserSchema, UserUpdateSchema
from security import (
    generate_confirmation_token,
    get_current_user,
    get_google_user_info,
    get_password_hash,
    send_email,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from templates import create_confirmation_email_template, create_password_reset_email_template

sys.path.append("..")

router = APIRouter(prefix="/users", tags=["users"])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):
    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Username already exists",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already exists",
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone_number=user.phone_number,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    token = generate_confirmation_token(user.email)
    confirm_url = f"{settings.BASE_URL}/email-confirmated/{token}"
    subject, body = create_confirmation_email_template(
        f"{user.first_name} {user.last_name}", confirm_url
    )

    send_email(subject, user.email, body)

    return db_user


@router.post("/google", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user_google(session: Session):
    code = login_google()

    user_info = get_google_user_info(code)

    user = UserSchema(
        email=user_info.get("email"),
        first_name=user_info.get("given_name"),
        last_name=user_info.get("family_name"),
        username=user_info.get("email"),
        phone_number=user_info.get("phone_number", "Não disponível"),
    )

    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Username already exists",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already exists",
            )

    hashed_password = get_password_hash(secrets.token_hex(16))

    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone_number=user.phone_number,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    token = generate_confirmation_token(user.email)
    reset_url = f"{settings.BASE_URL}/auth/new-password/{token}"
    subject, body = create_password_reset_email_template(
        f"{user.first_name} {user.last_name}", reset_url
    )

    send_email(subject, user.email, body)

    return db_user


@router.get("/{user_id}", response_model=UserPublic)
def read_user(user_id: int, session: Session):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    return user


@router.get("/", response_model=UserList)
def read_users(session: Session, skip: int = 0, limit: int = 100):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {"users": users}


@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserUpdateSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    current_user.email = user.email
    current_user.phone_number = user.phone_number
    session.commit()
    session.refresh(current_user)

    return current_user


@router.put("/new-password/{email}", response_model=Message)
def new_password(
    email: str,
    session: Session,
):
    user = session.scalar(select(User).where(User.email == email))

    token = generate_confirmation_token(user.email)
    reset_url = f"{settings.BASE_URL}/new-password/{token}"
    subject, body = create_password_reset_email_template(
        f"{user.first_name} {user.last_name}", reset_url
    )

    send_email(subject, user.email, body)

    return {"message": "Password reset email sent"}


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    session.delete(current_user)
    session.commit()

    return {"message": "User deleted"}
