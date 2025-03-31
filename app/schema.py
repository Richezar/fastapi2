from pydantic import BaseModel
from datetime import datetime
import uuid

class IdResponse(BaseModel):
    id: int

class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: float

class CreateAdvertisementResponse(BaseModel):
    id: int

class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None

class DeleteAdvertisementResponse(BaseModel):
    status: str

class GetAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner: str
    date_created: datetime
    owner_id: int

class LoginRequest(BaseModel):
    name: str
    password: str

class LoginResponse(BaseModel):
    token: uuid.UUID

class CreateUserRequest(BaseModel):
    name: str
    password: str

class CreateUserResponse(IdResponse):
    pass

class GetUserResponse(BaseModel):
    id: int
    name: str

class UpdateUserRequest(BaseModel):
    name: str | None = None
    password: str | None = None

class DeleteUserResponse(BaseModel):
    status: str

