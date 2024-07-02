from sqlalchemy import Boolean, Column, Integer, String

from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True)
    username = Column(String(200), unique=True, index=True)
    first_name = Column(String(200))
    last_name = Column(String(225))
    hashed_password = Column(String(225))
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(225))
    # address_id = Column(Integer, ForeignKey('address.id'), nullable=True)

    # address = relationship('address', back_populates='owner')
