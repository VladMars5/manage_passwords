from datetime import datetime
from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, Table, Identity
from database import metadata

user = Table(
    "user",
    metadata,
    Column("id", Integer, Identity(), nullable=False, unique=True),
    Column("email", String(length=256), nullable=False, primary_key=True),
    Column("username", String(length=128), nullable=False, unique=True),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("password", String(length=1024), nullable=False),
    Column("is_active", Boolean, server_default='false', nullable=False),
    Column("is_verified", Boolean, server_default='false', nullable=False),
    Column("phone", String),
)
