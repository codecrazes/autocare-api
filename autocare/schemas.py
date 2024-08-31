from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str


class UserUpdateSchema(BaseModel):
    email: EmailStr
    phone_number: str


class UserPublic(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class VehicleSchema(BaseModel):
    brand: str
    model: str
    year: int


class VehiclePublic(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class VehicleList(BaseModel):
    vehicles: list[VehiclePublic]


class VehicleProblemSchema(BaseModel):
    vehicle_id: int
    description: str


class VehicleProblemPublic(BaseModel):
    id: int
    vehicle_id: int
    description: str
    model_config = ConfigDict(from_attributes=True)


class VehicleProblemList(BaseModel):
    problems: list[VehicleProblemPublic]


class AddressSchema(BaseModel):
    user_id: int
    street: str
    number: str
    city: str
    state: str
    zip_code: str


class AddressPublic(BaseModel):
    id: int
    user_id: int
    street: str
    number: str
    city: str
    state: str
    zip_code: str
    model_config = ConfigDict(from_attributes=True)
