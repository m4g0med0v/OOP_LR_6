import logging
from pathlib import Path

import pytest

from src.individual_task_1 import (
    connect_db,
)


@pytest.fixture(scope="session")
def setup_db():
    """Создание временной базы данных перед каждым тестом."""
    test_db = "test_trains"
    conn = connect_db(test_db)
    yield conn
    conn.close()
    db_path = Path(f"data/{test_db}.db")
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(autouse=True)
def disable_logging():
    """Отключение логирования во время тестов."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
