import logging
from contextlib import contextmanager
from logging import Logger
from typing import Any, Dict, Generator, Optional, Self

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from auth_service.core.configurations import DatabaseConfig
from auth_service.infrastructure.postgresql.database.models import Base


class Database:
    def __init__(self, config: DatabaseConfig, logger: Optional[Logger] = None) -> None:
        self._config: DatabaseConfig = config
        self._logger: Logger = logger or logging.getLogger(__name__)
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker[Session]] = None
        self._initialize()

    def _initialize(self) -> None:
        try:
            dsn: str = self._config.dsn
            engine_options: Dict[str, Any] = self._config.engine_options

            self._engine = create_engine(dsn, **engine_options)
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )

            self._logger.info("Database connection initialized.")

        except Exception as e:
            self._logger.error(f"Failed to initialize database: {e}")
            raise

    def get_engine(self) -> Engine:
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine

    def get_session(self) -> Session:
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")
        return self._session_factory()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        session: Session = self.get_session()
        try:
            yield session
            session.commit()
            self._logger.debug("Transaction committed successfully")
        except Exception as e:
            session.rollback()
            self._logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        try:
            with self.get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            self._logger.debug("Database health check passed")
            return True
        except Exception as e:
            self._logger.error(f"Database health check failed: {e}")
            return False

    def dispose(self) -> None:
        if self._engine:
            self._engine.dispose()
            self._logger.info("Database connections disposed")

    def create_tables(self, base: Any = Base) -> None:
        try:
            base.metadata.create_all(self.get_engine())
            self._logger.info("All tables created successfully")
        except Exception as e:
            self._logger.error(f"Failed to create tables: {e}")
            raise

    def drop_tables(self, base: Any = Base) -> None:
        try:
            base.metadata.drop_all(self.get_engine())
            self._logger.info("All tables dropped successfully")
        except Exception as e:
            self._logger.error(f"Failed to drop tables: {e}")
            raise

    def create_table(self, table_name: str) -> None:
        try:
            table: Any = Base.metadata.tables.get(table_name)
            if table is not None:
                table.create(self.get_engine(), checkfirst=True)
                self._logger.info(f"Table '{table_name}' created successfully")
            else:
                self._logger.warning(f"Table '{table_name}' not found in metadata")
        except Exception as e:
            self._logger.error(f"Failed to create table '{table_name}': {e}")
            raise

    def drop_table(self, table_name: str) -> None:
        try:
            table: Any = Base.metadata.tables.get(table_name)
            if table is not None:
                table.drop(self.get_engine(), checkfirst=True)
                self._logger.info(f"Table '{table_name}' dropped successfully")
            else:
                self._logger.warning(f"Table '{table_name}' not found in metadata")
        except Exception as e:
            self._logger.error(f"Failed to drop table '{table_name}': {e}")
            raise

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.dispose()
