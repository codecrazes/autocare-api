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
    street: str
    neighborhood: str
    number: str
    city: str
    state: str
    zip_code: str


class AddressPublic(BaseModel):
    id: int
    street: str
    neighborhood: str
    number: str
    city: str
    state: str
    zip_code: str
    model_config = ConfigDict(from_attributes=True)


class ProblemDetailSchema(BaseModel):
    description: str
    service: str
    price: str
    price_details: str


class DiagnosisSchema(BaseModel):
    id: int
    vehicle_problem_id: int
    symptoms: str
    predicted_problem: str
    problem_details: ProblemDetailSchema


class DiagnosisCreate(BaseModel):
    vehicle_problem_id: int
    vehicle_id: int
    symptoms: list[str]


class DiagnosisPublic(BaseModel):
    id: int
    vehicle_problem_id: int
    user_id: int
    symptoms: str
    predicted_problem: str
    problem_details: ProblemDetailSchema
    model_config = ConfigDict(from_attributes=True)


class MechanicSchema(BaseModel):
    name: str
    image: str
    rating: float
    open24hrs: bool
    wifi: bool
    take_and_deliver: bool
    accessible: bool
    waiting_room: bool
    address: AddressSchema
    available_services: str
    specialties: str


class MechanicPublic(BaseModel):
    id: int
    name: str
    image: str
    rating: float
    open24hrs: bool
    wifi: bool
    take_and_deliver: bool
    accessible_: bool
    waiting_room: bool
    available_services: str
    specialties: str
    address: str
    model_config = ConfigDict(from_attributes=True)


class BookingSchema(BaseModel):
    mechanic_id: int
    date: str
    service: str
    price: str
    status: str


class BookingPublic(BaseModel):
    id: int
    user_id: int
    mechanic_id: int
    date: str
    service: str
    price: str
    status: str
    model_config = ConfigDict(from_attributes=True)
