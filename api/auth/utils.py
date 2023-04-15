from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import JWT_SECRET_KEY, JWT_ALGORITHM
from database import get_async_session
from auth.models import user as user_model


async def get_current_user(
        token: str = Depends(OAuth2PasswordBearer(tokenUrl='auth/login')),
        session: AsyncSession = Depends(get_async_session)) -> user_model:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get('sub')
        if username is None:
            AuthHelper.raise_auth_exception('Could not validate credentials')
        query = select(user_model).where(user_model.c.username == username)
        user = await session.execute(query)
        user = user.fetchone()
        if not user:
            AuthHelper.raise_auth_exception('Could not validate credentials')
        if user.is_active is False:
            AuthHelper.raise_auth_exception('User is blocked')
    except JWTError as e:
        AuthHelper.raise_auth_exception(str(e))
    else:
        return user


class AuthHelper:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

    @staticmethod
    def hash_password(password: str) -> str:
        return AuthHelper.pwd_context.hash(password)

    @staticmethod
    def raise_auth_exception(message: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return AuthHelper.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()

        to_encode.update({
            'exp': datetime.utcnow() + expires_delta
        })

        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
