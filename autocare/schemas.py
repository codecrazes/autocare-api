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
