import re

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException


def valid_email(email: str) -> str:
    if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email):
        raise ValueError('Invalid Email')
    return email


def valid_username(username: str) -> str:
    if not all(x.isdigit() or x.isalpha() for x in username):
        raise ValueError('Nickname must contain only letters and numbers')
    elif username[0].isdigit():
        raise ValueError('Nickname cannot start with a number')
    return username


def valid_password(password: str) -> str:
    if password.isalpha() or password.isdigit():
        raise ValueError('Password must not consist of only letters or numbers')
    return password


def valid_phone(phone: str | None) -> str | None:
    if phone is None:
        return phone
    try:
        if not phonenumbers.is_valid_number(phonenumbers.parse(phone)):
            raise ValueError('Invalid phone number')
    except NumberParseException as err:
        raise ValueError(err)
    return phone
