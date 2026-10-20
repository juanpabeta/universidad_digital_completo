"""Migration environment; credentials come from process configuration."""

from alembic import context

from app.core.database import Base, engine
import app.core.models  # noqa: F401 - register all mapped classes


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
