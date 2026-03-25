#  type: ignore

from alembic import config, script
from alembic.runtime import migration

from src.db.engine import engine
from src.main.logging import get_logger

logger = get_logger(__name__)


def check_migration_head() -> bool:
    alembic_cfg = config.Config("./src/db/alembic.ini")
    dir = script.ScriptDirectory.from_config(alembic_cfg)
    with engine.begin() as connection:
        ctx = migration.MigrationContext.configure(connection)
        return set(ctx.get_current_heads()) == set(dir.get_heads())


def main():
    logger.info("Checking migrations head")
    is_migration_head_latest = check_migration_head()
    if not is_migration_head_latest:
        raise Exception("Migration head is not latest")
    logger.info("Head is latest")


if __name__ == "__main__":
    main()
