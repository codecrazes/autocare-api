from datetime import datetime
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry
from sqlalchemy.orm import relationship
from sqlalchemy import String

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column(String(15))
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=False)

    adrress: Mapped["Adrress"] = relationship(back_populates="user")
    vehicle_infomation: Mapped["Vehicle_Information"] = relationship(back_populates="user")

class Address:
    __tablename__ = "adrress"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    local: Mapped[str] = mapped_column(String(70))
    number: Mapped[int] = mapped_column()
    neighbornhoodi: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    state: Mapped[str] = mapped_column(String(50))
    postal_code: Mapped[str] = mapped_column()
    
    user: Mapped["User"] = relationship(back_populates="address")
    mechanics: Mapped["Mechanics"] = relationship(back_populates="address")


class Mechanics:
    __tablename__ = "mechanics"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name_mechanics: Mapped[str] = mapped_column(String(50))
    cnpj: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    open_mechanics: Mapped[datetime] = mapped_column()
    close_mechanics: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(initi=False, sever_default=func.now())

    user: Mapped["User"] = relationship(back_populates="mechanics")
         

class Veicle_Information:
    __tablename__ = "veicle_information"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    brand: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(20))
    year: Mapped[int] = mapped_column()
    license_plate: Mapped[str] = mapped_column(String(20))
    chassis: Mapped[str] = mapped_column(String(20))
    current_mileage: Mapped[int] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="veicle_information")


class Service_Detais:
    __tablebname__ = "service_detais"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    service_date: Mapped[datetime] = mapped_column()
    service_description: Mapped[str] = mapped_column()
    reason_for_service: Mapped[str] = mapped_column()

    mechanics: Mapped["Mechanics"] = relationship(back_populates="addresses")


class Diagnosis:
    __tablename__ = "diagnosis"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    indentifield_issues: Mapped[str] = mapped_column(String(150))
    causes: Mapped[str] = mapped_column(String(150))
    solutions: Mapped[str] = mapped_column(String(150))

    service_detais: Mapped["Service_Detais"] = relationship(back_populates="diagnosis")

class Payment:
    __tablename__ = "payment"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    total_service: Mapped[str] = mapped_column(String(15))
    intallment_plan: Mapped[int] = mapped_column()
    payment_date: Mapped[datetime] = mapped_column()
    payment_method: Mapped[str] = mapped_column(String(15))

    service_detais: Mapped["Service_Detais"] = relationship(back_populates="payment")


    
    



