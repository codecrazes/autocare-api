import sys
from http import HTTPStatus
from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import User, Vehicle
from schemas import VehicleList, VehiclePublic, VehicleSchema
from security import (
    get_current_user,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.append("..")

router = APIRouter(prefix="/vehicle", tags=["vehicles"])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=VehiclePublic)
def create_vehicle(vehicle: VehicleSchema, session: Session, user: CurrentUser):
    db_vehicle = Vehicle(
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        user_id=user.id,
    )

    session.add(db_vehicle)
    session.commit()
    session.refresh(db_vehicle)

    return db_vehicle


@router.get("/", response_model=VehiclePublic)
def get_vehicle(vehicle_id: int, session: Session, user: CurrentUser):
    db_vehicle = session.get(Vehicle, vehicle_id)

    if not db_vehicle:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

    if user.id != db_vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    return db_vehicle


@router.get("/list", response_model=VehicleList)
def list_vehicles(session: Session, user: CurrentUser):
    db_vehicles = session.execute(select(Vehicle).where(Vehicle.user_id == user.id)).scalars().all()

    return {"vehicles": db_vehicles}


@router.put("/", response_model=VehiclePublic)
def update_vehicle(vehicle: VehiclePublic, session: Session, user: CurrentUser):
    db_vehicle = session.get(Vehicle, vehicle.id)

    if not db_vehicle:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

    if db_vehicle.user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    db_vehicle.brand = vehicle.brand
    db_vehicle.model = vehicle.model
    db_vehicle.year = vehicle.year

    session.commit()
    session.refresh(db_vehicle)

    return db_vehicle


@router.delete("/")
def delete_vehicle(vehicle_id: int, session: Session, user: CurrentUser):
    db_vehicle = session.get(Vehicle, vehicle_id)

    if not db_vehicle:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

    if db_vehicle.user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    session.delete(db_vehicle)
    session.commit()

    return {"message": "Vehicle deleted"}
