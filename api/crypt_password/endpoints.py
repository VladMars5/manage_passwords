from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select, delete, and_
from sqlalchemy.exc import IntegrityError

from crypt_password.models import group_password_table, password_table
from auth.models import user as user_model
from database import get_async_session
from auth.utils import get_current_user
from crypt_password.utils import generate_password, check_auth_data_by_user, check_group_by_user, decrypt_password
from crypt_password.schemas import NewGroup, UpdateGroup, AuthDataGroup, NewAuthData, UpdateAuthData, DecryptAuthData,\
    SearchData, SearchedAuthData, AllGroups, AuthDataByGroup

router = APIRouter()


@router.post('/create_group')
async def create_group(group: NewGroup,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: user_model = Depends(get_current_user))\
        -> JSONResponse:
    """ Добавить новую группу паролей """
    group = group.dict()
    group.update({'user_id': current_user.id})
    try:
        stmt = insert(group_password_table).values(**group)
        await session.execute(stmt)
        await session.commit()
        message, status_code, error = f"Successfully created group ({group.get('name')}) " \
                                      f"for User {current_user.username}", status.HTTP_201_CREATED, None
    except IntegrityError as ex:
        message, status_code, error = f"Group by Name -> {group.get('name')} for User {current_user.username} " \
                                      f"already exists. Change name group", status.HTTP_409_CONFLICT, ex
    return JSONResponse(
        content={'message': message, 'error': str(error)},
        status_code=status_code,
    )


@router.put('/update_group')
async def update_group(data_group: UpdateGroup,
                       session: AsyncSession = Depends(get_async_session),
                       current_user: user_model = Depends(get_current_user)) -> JSONResponse:
    """ Обновить данные группы """
    if not await check_group_by_user(session=session, user_id=current_user.id, group_id=data_group.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No found group by User ({current_user.username})',
        )
    data_group = data_group.dict()
    try:
        stmt = update(group_password_table)\
            .where(group_password_table.c.id == data_group.get('id')).values(**data_group)
        await session.execute(stmt)
        await session.commit()
        data_group.pop('id')
        message, status_code, error = f"Successfully update group ({data_group}) " \
                                      f"for User {current_user.username}", status.HTTP_200_OK, None
    except IntegrityError as ex:
        message, status_code, error = f"Group by Name -> {data_group.get('name')} for User {current_user.username} " \
                                      f"already exists. Change name group", status.HTTP_409_CONFLICT, ex
    return JSONResponse(
        content={'message': message, 'error': str(error)},
        status_code=status_code,
    )


@router.delete('/delete_group')
async def delete_group(group_id: Annotated[int, Query(gt=0)],
                       session: AsyncSession = Depends(get_async_session),
                       current_user: user_model = Depends(get_current_user)) -> JSONResponse:
    """ Удалить группу """
    stmt = delete(group_password_table).where(and_(group_password_table.c.id == group_id,
                                                   group_password_table.c.user_id == current_user.id))
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        content={'message': 'Group successfully delete'},
        status_code=status.HTTP_200_OK,
    )


@router.get('/get_all_my_groups', response_model=List[Optional[AllGroups]])
async def get_all_groups_user(session: AsyncSession = Depends(get_async_session),
                              current_user: user_model = Depends(get_current_user)) -> List[Optional[AllGroups]]:
    """ Получить все группы пользователя """
    query = select(group_password_table.c.id, group_password_table.c.name, group_password_table.c.description)\
        .where(group_password_table.c.user_id == current_user.id)
    all_groups = await session.execute(query)
    return [AllGroups(**group._mapping) for group in all_groups.all()]


@router.get('/get_data_groups', response_model=List[Optional[AuthDataGroup]])
async def get_auth_data_by_group(session: AsyncSession = Depends(get_async_session),
                                 current_user: user_model = Depends(get_current_user)) -> List[Optional[AuthDataGroup]]:
    """ Получить все записи из учетных данных по группам """
    query = select(group_password_table.c.id.label('group_id'),
                   group_password_table.c.name.label('group_name'),
                   group_password_table.c.description.label('group_description'),
                   password_table.c.id.label('auth_data_id'),
                   password_table.c.service_name,
                   password_table.c.login)\
        .join(password_table, password_table.c.group_id == group_password_table.c.id)\
        .where(group_password_table.c.user_id == current_user.id)
    auth_data_groups = await session.execute(query)
    return [AuthDataGroup(**auth_data._mapping) for auth_data in auth_data_groups.all()]


@router.post('/create_auth_data')
async def create_auth_data(auth_data: NewAuthData,
                           session: AsyncSession = Depends(get_async_session),
                           current_user: user_model = Depends(get_current_user)) -> JSONResponse:
    """ Добавить новый пароль в базу привязанный к группе """
    if not await check_group_by_user(session=session, user_id=current_user.id, group_id=auth_data.group_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No found group by User ({current_user.username}) AND GroupId ({auth_data.group_id})',
        )
    auth_data = auth_data.dict()
    try:
        stmt = insert(password_table).values(**auth_data)
        await session.execute(stmt)
        await session.commit()
        message, status_code, error = f"Successfully created auth_data ({auth_data.get('service_name')} " \
                                      f"and {auth_data.get('login')} ) " \
                                      f"for User {current_user.username}", status.HTTP_201_CREATED, None
    except IntegrityError as ex:
        message, status_code, error = f"Auth Data by ServiceName -> {auth_data.get('service_name')} " \
                                      f"and Login -> {auth_data.get('login')} for User {current_user.username} " \
                                      f"already exists.", status.HTTP_409_CONFLICT, ex
    except Exception as ex:
        message, status_code, error = "", status.HTTP_409_CONFLICT, ex
    return JSONResponse(
        content={'message': message, 'error': str(error)},
        status_code=status_code,
    )


@router.put('/update_auth_data')
async def update_auth_data(update_data: UpdateAuthData,
                           session: AsyncSession = Depends(get_async_session),
                           current_user: user_model = Depends(get_current_user)) -> JSONResponse:
    """ Обновить авторизационные данные """
    if not await check_auth_data_by_user(session=session, user_id=current_user.id, auth_data_id=update_data.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No found auth by User ({current_user.username}) and AuthDataId ({update_data.id})',
        )
    update_data = update_data.dict()
    try:
        stmt = update(password_table).where(password_table.c.id == update_data.get('id')).values(**update_data)
        await session.execute(stmt)
        await session.commit()
        update_data.pop('id')
        message, status_code, error = f"Successfully update auth_data ({update_data}) " \
                                      f"for User {current_user.username}", status.HTTP_200_OK, None
    except IntegrityError as ex:
        message, status_code, error = f"AuthData by ServiceName -> {update_data.get('service_name')} " \
                                      f"or Login {update_data.get('login')} for User {current_user.username} " \
                                      f"already exists. Change parameters", status.HTTP_409_CONFLICT, ex
    except Exception as ex:
        message, status_code, error = "", status.HTTP_409_CONFLICT, ex
    return JSONResponse(
        content={'message': message, 'error': str(error)},
        status_code=status_code,
    )


@router.delete('/delete_auth_data')
async def delete_auth_data(auth_data_id: Annotated[int, Query(gt=0)],
                           session: AsyncSession = Depends(get_async_session),
                           current_user: user_model = Depends(get_current_user)) -> JSONResponse:
    """ Удалить авторизационные данные """
    if not await check_auth_data_by_user(session=session, user_id=current_user.id, auth_data_id=auth_data_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No found auth_data by User ({current_user.username}) and AuthDataId ({auth_data_id})',
        )
    stmt = delete(password_table).where(password_table.c.id == auth_data_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(
        content={'message': 'AuthData successfully delete'},
        status_code=status.HTTP_200_OK,
    )


@router.get('/get_all_auth_data_by_group', response_model=List[Optional[AuthDataByGroup]])
async def get_all_auth_data_by_group(group_id: Annotated[int, Query(gt=0)],
                                     session: AsyncSession = Depends(get_async_session),
                                     current_user: user_model = Depends(get_current_user)) \
        -> List[Optional[AuthDataByGroup]]:
    """ Получить все авторизационные данные по id group """
    query = select(password_table.c.id, password_table.c.service_name, password_table.c.login) \
        .join(group_password_table, group_password_table.c.id == password_table.c.group_id) \
        .where(and_(group_password_table.c.user_id == current_user.id, group_password_table.c.id == group_id))
    auth_data_by_group = await session.execute(query)
    return [AuthDataByGroup(**auth_data._mapping) for auth_data in auth_data_by_group.all()]


@router.get('/decrypt_password', response_model=DecryptAuthData)
async def get_decrypt_password(auth_data_id: Annotated[int, Query(gt=0)],
                               session: AsyncSession = Depends(get_async_session),
                               current_user: user_model = Depends(get_current_user)) -> DecryptAuthData:
    """ Показать расшифрованный пароль по auth_data_id """
    if not await check_auth_data_by_user(session=session, user_id=current_user.id, auth_data_id=auth_data_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No found auth by User ({current_user.username}) and AuthDataId ({auth_data_id})',
        )
    query = select(password_table.c.hashed_password) \
        .join(group_password_table, group_password_table.c.id == password_table.c.group_id) \
        .where(and_(group_password_table.c.user_id == current_user.id, password_table.c.id == auth_data_id))
    auth_data = await session.execute(query)
    auth_data = auth_data.fetchone()
    return DecryptAuthData(auth_data_id=auth_data_id,
                           decrypt_password=decrypt_password(encrypted_password=auth_data.hashed_password))


#
@router.post('/search_auth_data', response_model=List[Optional[SearchedAuthData]])
async def search_auth_data(search_data: SearchData,
                           session: AsyncSession = Depends(get_async_session),
                           current_user: user_model = Depends(get_current_user)) -> List[Optional[SearchedAuthData]]:
    """ Поиск пароля по имени сервиса логину """
    query = select(group_password_table.c.name.label('group_name'),
                   password_table.c.id.label('auth_data_id'),
                   password_table.c.service_name,
                   password_table.c.login) \
        .join(password_table, password_table.c.group_id == group_password_table.c.id) \
        .filter(group_password_table.c.user_id == current_user.id)
    if search_data.login:
        query = query.filter(password_table.c.login.like(f'%{search_data.login}%'))
    if search_data.service_name:
        query = query.filter(password_table.c.service_name.like(f'%{search_data.service_name}%'))
    searched_auth_data = await session.execute(query)
    return [SearchedAuthData(**auth_data._mapping) for auth_data in searched_auth_data.all()]


@router.get('/generate_password')
async def generate_password_endpoint(length_password: int = Query(gt=6, le=30, default=12)) -> JSONResponse:
    """ Сгенерировать пароль """
    return JSONResponse(
        content={'generated_password': generate_password(length_password=length_password)},
        status_code=status.HTTP_200_OK,
    )
