from sqlalchemy import Column, Integer, String, Table, Identity, ForeignKey

from database import metadata


group_password_table = Table(
    "group",
    metadata,
    Column("id", Integer, Identity(), nullable=False, unique=True),
    Column("name", String(length=512), nullable=False, primary_key=True),
    Column("description", String(length=2048)),
    Column("user_id", Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, primary_key=True),
)


password_table = Table(
    "auth_data",
    metadata,
    Column("id", Integer, Identity(), nullable=False, unique=True),
    Column("service_name", String(length=512), nullable=False, primary_key=True),
    Column("login", String(length=128), nullable=False, primary_key=True),
    Column("hashed_password", String(length=2048), nullable=False),
    Column("group_id", Integer, ForeignKey('group.id', ondelete='CASCADE'), nullable=False, primary_key=True)
)
