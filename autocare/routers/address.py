import sys
from http import HTTPStatus
from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Address, User
from schemas import AddressPublic, AddressSchema
from security import (
    get_current_user,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.append("..")

router = APIRouter(prefix="/address", tags=["addresses"])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=AddressPublic)
def create_address(address: AddressSchema, session: Session, user: CurrentUser):
    existing_address = (
        session.execute(select(Address).where(Address.user_id == user.id)).scalars().first()
    )

    if existing_address:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="User already has an address"
        )

    db_address = Address(
        user_id=user.id,
        street=address.street,
        neighborhood=address.neighborhood,
        number=address.number,
        city=address.city,
        state=address.state,
        zip_code=address.zip_code,
    )

    session.add(db_address)
    session.commit()
    session.refresh(db_address)

    return db_address


@router.get("/", response_model=AddressPublic)
def get_address(session: Session, user: CurrentUser):
    db_address = (
        session.execute(select(Address).where(Address.user_id == user.id)).scalars().first()
    )

    if not db_address:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Address not found")

    return db_address


@router.put("/", response_model=AddressPublic)
def update_address(address: AddressSchema, session: Session, user: CurrentUser):
    db_address = (
        session.execute(select(Address).where(Address.user_id == user.id)).scalars().first()
    )

    if not db_address:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Address not found")

    db_address.street = address.street
    db_address.neighborhood = address.neighborhood
    db_address.number = address.number
    db_address.city = address.city
    db_address.state = address.state
    db_address.zip_code = address.zip_code

    session.commit()
    session.refresh(db_address)

    return db_address


@router.delete("/")
def delete_address(session: Session, user: CurrentUser):
    db_address = (
        session.execute(select(Address).where(Address.user_id == user.id)).scalars().first()
    )

    if not db_address:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Address not found")

    session.delete(db_address)
    session.commit()

    return {"message": "Address deleted"}
