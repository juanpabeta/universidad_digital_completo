"""Bootstrap command behavior checks."""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.core.models  # noqa: F401
from app.bootstrap import ROLES, main
from app.core.database import Base
from app.users.models import Role, User


def test_bootstrap_without_admin_credentials_only_seeds_roles(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr("app.bootstrap.SessionLocal", testing_session)
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    main()

    with testing_session() as db:
        role_names = {role.nombre for role in db.scalars(select(Role)).all()}
        assert role_names == set(ROLES)
        assert db.scalar(select(User.id_usuario)) is None
