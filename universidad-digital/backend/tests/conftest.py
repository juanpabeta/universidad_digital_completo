"""Isolated request tests with a transactional-looking disposable database."""

import os

os.environ.setdefault("DB_PASSWORD", "unused-in-sqlite-tests")
os.environ.setdefault("JWT_SECRET", "test-only-secret-of-at-least-32-characters")

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.core.models  # noqa: F401
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.users.models import Role, User


@pytest.fixture
def client() -> Generator[tuple[TestClient, dict[str, int]], None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory.begin() as db:
        roles = {
            name: Role(nombre=name, descripcion=name)
            for name in ("ADMINISTRADOR", "DOCENTE", "ESTUDIANTE")
        }
        db.add_all(roles.values())
        users = {
            name: User(
                nombres=name.title(), apellidos="Prueba",
                email=f"{name.lower()}@example.com",
                password_hash=hash_password("ClaveSegura123!"),
                roles=[roles[name]],
            )
            for name in roles
        }
        db.add_all(users.values())
        db.flush()
        ids = {name: user.id_usuario for name, user in users.items()}

    def override_db() -> Generator[Session, None, None]:
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as http:
        yield http, ids
    app.dependency_overrides.clear()
    engine.dispose()
