import inspect
import logging
import os
import re
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, MetaData

log = logging.getLogger(__name__)

try:
    from virtualspace import settings
    from virtualspace import models
    from virtualspace.models.base import BaseModel
except ImportError as e:
    log.debug(e)

    current_path = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(current_path, '..')
    sys.path.append(root)

    from virtualspace import settings
    from virtualspace import models
    from virtualspace.utils.models.base import BaseModel


USE_TWOPHASE = False

# Config is an alembic .ini file with configuration.
config = context.config

fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')
db_names = config.get_main_option('databases')

config.set_section_option('dev', 'url', settings.DB_DEV_URL)
config.set_section_option('test', 'url', settings.DB_TEST_URL)


def get_all_models_metadata():
    metadata = list()

    for name, class_ in inspect.getmembers(models):
        if inspect.isclass(class_) and issubclass(class_, BaseModel):
            metadata.append(class_.metadata)

    return metadata


def combine_metadata(*args):
    m = MetaData()
    for metadata in args:
        for t in metadata.tables.values():
            t.tometadata(m)
    return m


target_metadata = {
    'dev': combine_metadata(*get_all_models_metadata()),
    'test': combine_metadata(*get_all_models_metadata())
}


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    # for the --sql use case, run migrations for each URL into
    # individual files.
    engines = {}

    for name in re.split(r',\s*', db_names):
        engines[name] = rec = {}
        rec['url'] = context.config.get_section_option(name, 'sqlalchemy.url')

    for name, rec in engines.items():
        logger.info('Migrating database %s' % name)
        file_ = '%s.sql' % name
        logger.info('Writing output to %s' % file_)
        with open(file_, 'w') as buffer:
            context.configure(
                url=rec['url'], output_buffer=buffer,
                target_metadata=target_metadata.get(name),
                literal_binds=True
            )
            with context.begin_transaction():
                context.run_migrations(engine_name=name)


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # for the direct-to-DB use case, start a transaction on all
    # engines, then run all migrations, then commit all transactions.
    engines = {}

    for name in re.split(r',\s*', db_names):
        engines[name] = rec = {}
        rec['engine'] = engine_from_config(
            context.config.get_section(name),
            prefix='sqlalchemy.',
            poolclass=pool.NullPool
        )

    for name, rec in engines.items():
        engine = rec['engine']
        rec['connection'] = conn = engine.connect()

        if USE_TWOPHASE:
            rec['transaction'] = conn.begin_twophase()
        else:
            rec['transaction'] = conn.begin()

    try:
        for name, rec in engines.items():
            logger.info('Migrating database %s' % name)
            context.configure(
                connection=rec['connection'],
                upgrade_token='%s_upgrades' % name,
                downgrade_token='%s_downgrades' % name,
                target_metadata=target_metadata.get(name)
            )
            context.run_migrations(engine_name=name)

        if USE_TWOPHASE:
            for rec in engines.values():
                rec['transaction'].prepare()

        for rec in engines.values():
            rec['transaction'].commit()
    except:
        for rec in engines.values():
            rec['transaction'].rollback()
        raise
    finally:
        for rec in engines.values():
            rec['connection'].close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
