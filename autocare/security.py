import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import HTTPStatus

from conf.settings import Settings
from database import get_session
from fastapi import Depends, HTTPException
from itsdangerous import URLSafeTimedSerializer
from jwt import DecodeError, decode, encode
from models import User
from pwdlib import PasswordHash
from schemas import TokenData
from sqlalchemy import select
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
from fastapi.security import OAuth2PasswordBearer

settings = Settings()
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def send_email(subject: str, recipient: str, body: str):
    message = MIMEMultipart()
    message["From"] = settings.SENDER_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, recipient, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")


serializer = URLSafeTimedSerializer(settings.CONFIRMATION_SECRET_KEY)


def generate_confirmation_token(email):
    return serializer.dumps(email, salt=settings.CONFIRMATION_SECRET_KEY)


def confirm_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt=settings.CONFIRMATION_SECRET_KEY, max_age=expiration)
    except Exception:
        return False

    return email


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except DecodeError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == token_data.username))

    if user is None:
        raise credentials_exception

    return user
