from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=False)

    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="user")
    addresses: Mapped[List["Address"]] = relationship("Address", back_populates="user")


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    street: Mapped[str] = mapped_column()
    neighborhood: Mapped[str] = mapped_column()
    number: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    zip_code: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="addresses")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    brand: Mapped[str] = mapped_column()
    model: Mapped[str] = mapped_column()
    year: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="vehicles")
    problems: Mapped[List["VehicleProblem"]] = relationship(
        "VehicleProblem", back_populates="vehicle"
    )


class VehicleProblem(Base):
    __tablename__ = "vehicle_problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    description: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    vehicle: Mapped[Vehicle] = relationship("Vehicle", back_populates="problems")


class Diagnosis(Base):
    __tablename__ = "diagnosis"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_problem_id: Mapped[int] = mapped_column(ForeignKey("vehicle_problems.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    symptoms: Mapped[str] = mapped_column()
    predicted_problem: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    service: Mapped[str] = mapped_column()
    price: Mapped[str] = mapped_column()
    price_details: Mapped[str] = mapped_column()


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column()
    open24hrs: Mapped[bool] = mapped_column()
    wifi: Mapped[bool] = mapped_column()
    take_and_deliver: Mapped[bool] = mapped_column()
    accessible_: Mapped[bool] = mapped_column()
    waiting_room: Mapped[bool] = mapped_column()
    address: Mapped[str] = mapped_column()
    available_services: Mapped[str] = mapped_column()
    specialties: Mapped[str] = mapped_column()


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    mechanic_id: Mapped[int] = mapped_column(ForeignKey("mechanics.id"))
    date: Mapped[datetime] = mapped_column()
    service: Mapped[str] = mapped_column()
    price: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
