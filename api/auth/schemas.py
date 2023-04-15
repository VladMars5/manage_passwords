from pydantic import BaseModel, root_validator
from typing import Optional
from datetime import datetime


class UserInToken(BaseModel):
    access_token: str
    token_type: str = 'Bearer'


class UserInfo(BaseModel):
    email: str
    username: str
    registered_at: Optional[datetime] = 'unknown'
    is_active: bool
    is_verified: bool
    phone: str | None


class CreateUser(BaseModel):
    email: str
    username: str
    password: str


class UpdateUser(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None


class ResetPassword(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None

    @root_validator
    def check_params_validate(cls, values):
        if not (values.get('email') or values.get('username')):
            raise ValueError("Specify Email or Username by Account!")
        return values


class NewPassword(BaseModel):
    new_password: str


class ChangeOldPassword(BaseModel):
    old_password: str
    new_password: str


class DeleteUser(BaseModel):
    password: str
