import sys
from http import HTTPStatus
from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import User, Vehicle, VehicleProblem
from schemas import VehicleProblemList, VehicleProblemPublic, VehicleProblemSchema
from security import (
    get_current_user,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.append("..")

router = APIRouter(prefix="/problem", tags=["problems"])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=VehicleProblemPublic)
def create_problem(problem: VehicleProblemSchema, session: Session, user: CurrentUser):
    vehicle = session.get(Vehicle, problem.vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Vehicle not found")

    if user.id != vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    db_problem = VehicleProblem(
        description=problem.description,
        vehicle_id=problem.vehicle_id,
    )

    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)

    return db_problem


@router.get("/", response_model=VehicleProblemPublic)
def get_problem(problem_id: int, session: Session, user: CurrentUser):
    db_problem = session.get(VehicleProblem, problem_id)

    if not db_problem:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Problem not found")

    vehicle = session.get(Vehicle, db_problem.vehicle_id)

    if user.id != vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    return db_problem


@router.put("/", response_model=VehicleProblemPublic)
def update_problem(problem: VehicleProblemPublic, session: Session, user: CurrentUser):
    db_problem = session.get(VehicleProblem, problem.id)

    if not db_problem:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Problem not found")

    vehicle = session.get(Vehicle, db_problem.vehicle_id)

    if user.id != vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    db_problem.description = problem.description

    session.commit()
    session.refresh(db_problem)

    return db_problem


@router.delete("/")
def delete_problem(problem_id: int, session: Session, user: CurrentUser):
    db_problem = session.get(VehicleProblem, problem_id)

    if not db_problem:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Problem not found")

    vehicle = session.get(Vehicle, db_problem.vehicle_id)

    if user.id != vehicle.user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not enough permissions")

    session.delete(db_problem)
    session.commit()

    return {"message": "Problem deleted successfully"}


@router.get("/list", response_model=VehicleProblemList)
def list_problems(session: Session, user: CurrentUser):
    db_problems = (
        session.execute(select(VehicleProblem).join(Vehicle).where(Vehicle.user_id == user.id))
        .scalars()
        .all()
    )

    return {"problems": db_problems}
