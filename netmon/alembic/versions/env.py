import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic config
config = context.config

# .env / ortamdan DB_URL al; yoksa sqlite fallback
db_url = os.getenv("DB_URL", None)
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Logging config (opsiyonel)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Eğer modellerin metadata'sını bağlamak istersen ileride import edip set edebilirsin.
target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
