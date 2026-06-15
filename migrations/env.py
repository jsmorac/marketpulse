import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# PRIMERO defines config, LUEGO lo usas
config = context.config

config.set_section_option("alembic", "DB_USER", os.environ["DB_USER"])
config.set_section_option("alembic", "DB_PASSWORD", os.environ["DB_PASSWORD"])
config.set_section_option("alembic", "DB_HOST", os.environ.get("DB_HOST", "localhost"))
config.set_section_option("alembic", "DB_PORT", os.environ.get("DB_PORT", "5432"))
config.set_section_option("alembic", "DB_NAME", os.environ["DB_NAME"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name, encoding="utf-8")

target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
