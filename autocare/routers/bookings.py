from http import HTTPStatus
import sys
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from conf.settings import Settings
from sqlalchemy.orm import Session
from schemas import BookingPublic, BookingSchema
from security import get_current_user
from database import get_session
from models import Bookings, User
from datetime import datetime


sys.path.append("..")
settings = Settings()

router = APIRouter(prefix="/bookings", tags=["bookings"])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=BookingPublic)
def create_booking(booking: BookingSchema, session: Session, user: CurrentUser):
    booking_date = datetime.fromisoformat(booking.date)

    if booking_date <= datetime.now():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Cannot book a date in the past or at the current time",
        )

    # existing_user_booking = (
    #     session.query(Bookings)
    #     .filter(
    #         Bookings.user_id == user.id,
    #         Bookings.status == "pending"
    #     )
    #     .first()
    # )

    # if existing_user_booking:
    #     raise HTTPException(
    #         status_code=HTTPStatus.CONFLICT,
    #         detail="User already has a booking for the selected date and mechanic",
    #     )

    existing_mechanic_booking = (
        session.query(Bookings)
        .filter(Bookings.mechanic_id == booking.mechanic_id, Bookings.date == booking.date)
        .first()
    )

    if existing_mechanic_booking:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="This date is already booked for the selected mechanic",
        )

    db_booking = Bookings(
        user_id=user.id,
        mechanic_id=booking.mechanic_id,
        date=booking.date,
        service=booking.service,
        price=booking.price,
        status=booking.status,
    )

    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)

    return jsonable_encoder(db_booking)


@router.get("/workshop/{workshop_id}", response_model=list[BookingPublic])
def get_bookings_by_workshop(workshop_id: int, session: Session, user: CurrentUser):
    db_bookings = session.query(Bookings).filter(Bookings.mechanic_id == workshop_id).all()

    if not db_bookings:
        return []

    return jsonable_encoder(db_bookings)


@router.delete("/{booking_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_booking(booking_id: int, session: Session, user: CurrentUser):
    db_booking = session.get(Bookings, booking_id)

    if not db_booking:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Booking not found")

    if db_booking.user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="User not authorized")

    session.delete(db_booking)
    session.commit()


@router.get("/user", response_model=list[BookingPublic])
def get_bookings_by_user(session: Session, user: CurrentUser):
    db_bookings = session.query(Bookings).filter(Bookings.user_id == user.id).all()

    if not db_bookings:
        return []

    return jsonable_encoder(db_bookings)
