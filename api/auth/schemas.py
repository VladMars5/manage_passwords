from typing import Optional
from datetime import datetime

from pydantic import BaseModel, root_validator, validator, Field

from auth.validators import valid_username, valid_email, valid_phone, valid_password


class UserInToken(BaseModel):
    access_token: str
    token_type: str = 'Bearer'


class UserInfo(BaseModel):
    email: str
    username: str
    registered_at: Optional[datetime]
    is_active: bool
    is_verified: bool
    phone: Optional[str]


class CreateUser(BaseModel):
    email: str = Field(max_length=100)
    username: str = Field(max_length=15, min_length=3)
    password: str = Field(min_length=10, max_length=30)
    confirmed_password: str = Field(min_length=10, max_length=30)
    phone: Optional[str]

    _valid_email = validator('email', allow_reuse=True)(valid_email)
    _valid_username = validator('username', allow_reuse=True)(valid_username)
    _valid_password = validator('password', allow_reuse=True)(valid_password)
    _valid_phone = validator('phone', allow_reuse=True)(valid_phone)

    @root_validator
    @classmethod
    def password_match(cls, values):
        if values.get('password') != values.get('confirmed_password'):
            raise ValueError('Password mismatch!')
        del values['confirmed_password']
        values.update({'registered_at': datetime.utcnow(), 'is_active': True, 'is_verified': False})
        return values


class UpdateUser(BaseModel):
    username: Optional[str] = Field(max_length=15, min_length=3)
    phone: Optional[str]

    @root_validator
    @classmethod
    def password_match(cls, values):
        if not (values.get('username') or values.get('phone')):
            raise ValueError('No parameters specified for update.')
        if values.get('username'):
            _ = valid_username(username=values.get('username'))
        if values.get('phone'):
            _ = valid_phone(phone=values.get('phone'))
        return {key: value for key, value in values.items() if value}


class ResetPassword(BaseModel):
    email: Optional[str] = Field(max_length=100)
    username: Optional[str] = Field(max_length=15, min_length=3)

    @root_validator
    @classmethod
    def password_match(cls, values):
        if not (values.get('username') or values.get('email')):
            raise ValueError('')

        if values.get('email'):
            _ = valid_email(email=values.get('email'))
        elif values.get('username'):
            _ = valid_username(username=values.get('username'))

        return values


class NewPassword(BaseModel):
    new_password: str = Field(max_length=30, min_length=10)
    confirmed_password: str = Field(max_length=30, min_length=10)

    _valid_password = validator('new_password', allow_reuse=True)(valid_password)

    @root_validator
    @classmethod
    def password_match(cls, values):
        if values.get('new_password') != values.get('confirmed_password'):
            raise ValueError('Password mismatch!')
        del values['confirmed_password']
        return values


class ChangeOldPassword(BaseModel):
    old_password: str = Field(max_length=30, min_length=10)
    new_password: str = Field(max_length=30, min_length=10)
    confirmed_password: str = Field(max_length=30, min_length=10)

    _valid_password = validator('new_password', allow_reuse=True)(valid_password)

    @root_validator
    @classmethod
    def password_match(cls, values):
        if values.get('new_password') != values.get('confirmed_password'):
            raise ValueError('Password mismatch!')
        del values['confirmed_password']
        return values


class DeleteUser(BaseModel):
    password: str = Field(max_length=30, min_length=10)
