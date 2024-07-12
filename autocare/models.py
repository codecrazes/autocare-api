from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=False)

class Address:
    __tablename__ = "adrress"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    local: Mapped[str] = mapped_column()
    number: Mapped[int] = mapped_column()
    neighbornhoodi: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    postal_code: Mapped[str] = mapped_column()

class Mechanics:
    __tablename__ = "mechanics"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    



