import sys
import os
from flask import current_app
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import logging

# This sets up logging with a fallback if the config is missing or incorrect
try:
    fileConfig(context.config.config_file_name)
except KeyError:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-5.5s [%(name)s] %(message)s")

print(f"Using Alembic config file: {context.config.config_file_name}")


# Add your project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app import app

# Alembic Config object
config = context.config

# # Configure logging
# fileConfig(config.config_file_name)

# Set SQLAlchemy URL and metadata
with app.app_context():
    config.set_main_option('sqlalchemy.url', current_app.config['SQLALCHEMY_DATABASE_URI'])
    target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
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