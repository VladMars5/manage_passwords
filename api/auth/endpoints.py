from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError
from celery_tasks.tasks import send_email
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_EXPIRE_MINUTES_RESET_PASSWORD
from auth.models import user as user_model
from database import get_async_session
from auth.utils import AuthHelper, get_current_user, private_full_email
from auth.schemas import UserInToken, UserInfo, CreateUser, ResetPassword, NewPassword, ChangeOldPassword, UpdateUser,\
    DeleteUser

router = APIRouter()


@router.post('/login', response_model=UserInToken)
async def authenticate_user(data_auth: OAuth2PasswordRequestForm = Depends(),
                            helper: AuthHelper = Depends(AuthHelper),
                            session: AsyncSession = Depends(get_async_session)
                            ) -> UserInToken:
    query = select(user_model).where(user_model.c.username == data_auth.username)
    user = await session.execute(query)
    user = user.fetchone()
    if not user:
        helper.raise_auth_exception('User doesnt exist')
    if helper.verify_password(data_auth.password, user.password) is False:
        helper.raise_auth_exception('Incorrect password')

    if user.is_active is False:
        helper.raise_auth_exception('User is not active')

    access_token = helper.create_access_token(
        data={'sub': user.username},
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES)
    )
    return UserInToken(access_token=access_token)


@router.get('/my_user', response_model=UserInfo)
async def get_current_user_endpoint(
    current_user: user_model = Depends(get_current_user),
) -> UserInfo:
    return UserInfo(**current_user._mapping)


@router.post('/create_user')
async def create_user(data_user: CreateUser,
                      session: AsyncSession = Depends(get_async_session),
                      auth_helper: AuthHelper = Depends(AuthHelper)) -> JSONResponse:
    data_user = data_user.dict()
    data_user['password'] = auth_helper.hash_password(data_user.get('password'))
    try:
        stmt = insert(user_model).values(**data_user)
        await session.execute(stmt)
        await session.commit()
        message, status_code = f'Successfully created user Email({data_user.get("email")}) ' \
                               f'Username({data_user.get("username")})', status.HTTP_201_CREATED
    except IntegrityError:
        message, status_code = 'User already exists. Change Email or Username.', status.HTTP_400_BAD_REQUEST
    return JSONResponse(
        content={'message': message},
        status_code=status_code,
    )


@router.put('/update_user/', response_model=UserInfo)
async def update_user(
    update_date: UpdateUser,
    current_user: user_model = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> UserInfo:
    stmt = update(user_model).where(user_model.c.username == current_user.username).values(**update_date.dict())
    await session.execute(stmt)
    await session.commit()
    user = dict(current_user._mapping)
    del user['password']
    user.update(update_date)
    return UserInfo(**user)


@router.get('/{username}/', response_model=UserInfo)
async def get_info(username: str, session: AsyncSession = Depends(get_async_session)) -> UserInfo:
    query = select(user_model).where(user_model.c.username == username)
    user = await session.execute(query)
    user = user.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No found user by username ({username})',
        )
    return UserInfo(**user._mapping)


@router.post('/reset_password/')
async def request_reset_password(login_data: ResetPassword, helper: AuthHelper = Depends(AuthHelper),
                                 session: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    if login_data.email:
        query = select(user_model.c.email, user_model.c.username,
                       user_model.c.is_active).where(user_model.c.email == login_data.email)
    else:
        query = select(user_model.c.email, user_model.c.username,
                       user_model.c.is_active).where(user_model.c.username == login_data.username)
    user = await session.execute(query)
    user = user.fetchone()
    if not user:
        return JSONResponse(
            content={'message': f'No found user by login '
                                f'({login_data.email if login_data.email else login_data.username})'},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if user.is_active is False:
        return JSONResponse(
            content={'message': f'User by Login(email={private_full_email(email=user.email)},'
                                f' username={user.username}) is not active.'},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    reset_token = helper.create_access_token(
        data={'username': user.username, 'type': 'reset_password'},
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES_RESET_PASSWORD)
    )
    send_email.delay(email=user.email, username=user.username, type_token='reset_password', token=reset_token)
    return JSONResponse(
            content={'message': f'Email sent to the address -> {private_full_email(email=user.email)}'},
            status_code=status.HTTP_200_OK,
        )


@router.post('/change_password/{token}')
async def recovery_by_token(token: str, new_password: NewPassword, helper: AuthHelper = Depends(AuthHelper),
                            session: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get('username')
        if str(payload.get('type')) != 'reset_password':
            return JSONResponse(
                content={'detail': f'Invalid Token'},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if username is None:
            return JSONResponse(
                content={'detail': f'No found data username by token.'},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        password = helper.hash_password(new_password.new_password)
        stmt = update(user_model).where(user_model.c.username == username).values(password=password)
        await session.execute(stmt)
        await session.commit()
        return JSONResponse(
            content={'message': f'Password by username ({username}) successfully updated.'},
            status_code=status.HTTP_200_OK,
        )
    except JWTError:
        return JSONResponse(
            content={'detail': f'Invalid Token'},
            status_code=status.HTTP_403_FORBIDDEN,
        )


@router.post('/change_old_password')
async def change_password(data_passwords: ChangeOldPassword, helper: AuthHelper = Depends(AuthHelper),
                          current_user: user_model = Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    if not helper.verify_password(data_passwords.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid old password!',
        )
    stmt = update(user_model).where(user_model.c.name == current_user.username).values(
        password=data_passwords.new_password)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        content={'message': f'Password by username ({current_user.username}) successfully updated.'},
        status_code=status.HTTP_200_OK,
    )


@router.delete('/delete_user')
async def delete_user(password_schemas: DeleteUser, helper: AuthHelper = Depends(AuthHelper),
                      current_user: user_model = Depends(get_current_user),
                      session: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    if not helper.verify_password(password_schemas.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid old password!',
        )
    stmt = delete(user_model).where(user_model.c.username == current_user.username)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        content={'message': f'Username ({current_user.username}) deleted.'},
        status_code=status.HTTP_200_OK,
    )


# TODO: добавить верификацию аккаунтов пользователей по email или телефону
