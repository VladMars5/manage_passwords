from cryptography.fernet import Fernet
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from config import ENCRYPTION_KEY, alphabet_password
from crypt_password.models import password_table, group_password_table

cipher_suite = Fernet(ENCRYPTION_KEY)


def encrypt_password(original_password: str) -> str:
    password = original_password.encode('utf-8')
    encrypted_password = cipher_suite.encrypt(password).decode('utf-8')
    return encrypted_password


def decrypt_password(encrypted_password: str) -> str:
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode('utf-8'))
    original_password = decrypted_password.decode('utf-8')
    return original_password


def generate_password(length_password: int = 12) -> str:
    length_password = 30 if length_password > 30 else length_password
    return ''.join([secrets.choice(alphabet_password) for _ in range(length_password)])


async def check_auth_data_by_user(session: AsyncSession, user_id: int, auth_data_id: int) -> bool:
    """ Проверка принадлежит ли пользователю пароль по id (auth_data) """
    query = select(password_table.c.id) \
        .join(group_password_table, group_password_table.c.id == password_table.c.group_id) \
        .where(and_(group_password_table.c.user_id == user_id, password_table.c.id == auth_data_id))
    auth_data = await session.execute(query)
    return bool(auth_data.fetchone())


async def check_group_by_user(session: AsyncSession, user_id: int, group_id: int) -> bool:
    """ Проверка принадлежит ли пользователю группа по id (group_id) """
    query = select(group_password_table.c.id) \
        .where(and_(group_password_table.c.user_id == user_id, group_password_table.c.id == group_id))
    auth_data = await session.execute(query)
    return bool(auth_data.fetchone())
