from typing import Optional

from pydantic import BaseModel, root_validator, Field
from crypt_password.utils import encrypt_password


class NewGroup(BaseModel):
    name: str = Field(max_length=512)
    description: Optional[str] = Field(max_length=2048)

    @root_validator
    @classmethod
    def validator_fields_create(cls, values):
        for key, value in values.items():
            values[key] = value.lower() if value else value
        return values


class UpdateGroup(BaseModel):
    id: int = Field(gt=0)
    name: Optional[str] = Field(max_length=512)
    description: Optional[str] = Field(max_length=2048)

    @root_validator
    @classmethod
    def validator_fields_update(cls, values):
        id_group = values.pop('id')
        if not any(values.values()):
            raise ValueError('At least one parameter must be filled')
        values = {key: value.lower() for key, value in values.items() if value}
        values['id'] = id_group
        return values


class AllGroups(BaseModel):
    id: int
    name: str
    description: Optional[str]


class AuthDataGroup(BaseModel):
    group_id: int
    group_name: str
    group_description: Optional[str]
    auth_data_id: int
    service_name: str
    login: str


class NewAuthData(BaseModel):
    service_name: str = Field(max_length=512)
    login: str = Field(max_length=128)
    password: str
    group_id: int = Field(gt=0)

    @root_validator
    @classmethod
    def validator_fields_create_auth_data(cls, values):
        values['service_name'] = values.get('service_name').lower()
        values['login'] = values.get('login').lower()
        values['hashed_password'] = encrypt_password(original_password=values.pop('password'))
        return values


class UpdateAuthData(BaseModel):
    id: int = Field(gt=0)
    service_name: Optional[str] = Field(max_length=512)
    login: Optional[str] = Field(max_length=128)
    password: Optional[str]

    @root_validator
    @classmethod
    def validator_fields_update_auth_data(cls, values):
        id_auth_data = values.pop('id')
        if not any(values.values()):
            raise ValueError('At least one parameter must be filled')
        values['hashed_password'] = encrypt_password(original_password=values.get('password')) \
            if values.get('password') else None
        values = {key: value.lower() for key, value in values.items() if value}
        values['id'] = id_auth_data
        return values


class AuthDataByGroup(BaseModel):
    id: int
    service_name: str
    login: str


class DecryptAuthData(BaseModel):
    auth_data_id: int
    decrypt_password: str


class SearchData(BaseModel):
    service_name: Optional[str] = Field(max_length=512)
    login: Optional[str] = Field(max_length=128)

    @root_validator
    @classmethod
    def validator_fields_search_auth_data(cls, values):
        if not any(values.values()):
            raise ValueError('At least one parameter must be filled')
        return values


class SearchedAuthData(BaseModel):
    group_name: str
    auth_data_id: int
    service_name: str
    login: str
