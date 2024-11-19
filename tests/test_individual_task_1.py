import logging
import unittest
from pathlib import Path

from src.individual_task_1 import (
    ConnectError,
    add_train,
    connect_db,
    find_train,
    list_trains,
)


class TestTrainManagement(unittest.TestCase):
    def setUp(self):
        """Создание временной базы данных перед каждым тестом."""
        self.test_db = "test_trains"
        self.conn = connect_db(self.test_db)

        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Удаление временной базы данных после каждого теста."""
        self.conn.close()
        db_path = Path(f"data/{self.test_db}.db")
        if db_path.exists():
            db_path.unlink()

        logging.disable(logging.NOTSET)

    @classmethod
    def setUpClass(cls) -> None:
        print(f"{cls.__name__:=^80}")

    @classmethod
    def tearDownClass(cls) -> None:
        print("=" * 80)

    def test_connect_db(self):
        """Тест успешного подключения к базе данных."""
        self.assertTrue(self.conn, "Соединение должно быть установлено.")

    def test_add_train_success(self):
        """Тест добавления нового поезда."""
        result = add_train(self.conn, "Москва", "001A", "10:00", "Киевский вокзал")
        self.assertIsNotNone(result, "Поезд должен быть успешно добавлен.")
        self.assertEqual(result[0], "001A", "Номер поезда должен совпадать.")

    def test_add_train_duplicate(self):
        """Тест добавления поезда с дублирующимся номером."""
        add_train(self.conn, "Москва", "001A", "10:00", "Киевский вокзал")
        result = add_train(self.conn, "Петербург", "001A", "12:00", "Ладожский вокзал")
        self.assertIsNone(result, "Добавление дублирующего поезда должно вернуть None.")

    def test_find_train_success(self):
        """Тест успешного поиска поезда по номеру."""
        add_train(self.conn, "Москва", "001A", "10:00", "Киевский вокзал")
        result = find_train(self.conn, "001A")
        self.assertIsNotNone(result, "Поезд должен быть найден.")
        self.assertEqual(result[1], "Москва", "Пункт назначения должен совпадать.")

    def test_find_train_not_found(self):
        """Тест поиска несуществующего поезда."""
        result = find_train(self.conn, "002B")
        self.assertIsNone(result, "Поезд с данным номером не должен быть найден.")

    def test_list_trains(self):
        """Тест получения списка поездов."""
        add_train(self.conn, "Москва", "001A", "10:00", "Киевский вокзал")
        add_train(self.conn, "Петербург", "002B", "12:00", "Ладожский вокзал")
        result = list_trains(self.conn)
        self.assertEqual(len(result), 2, "Список должен содержать два поезда.")
        self.assertEqual(result[0][0], "001A", "Номер первого поезда должен совпадать.")
        self.assertEqual(
            result[1][1],
            "Петербург",
            "Пункт назначения второго поезда должен совпадать.",
        )

    def test_connect_db_error(self):
        """Тест обработки ошибок при подключении к базе данных."""
        with self.assertRaises(ConnectError):
            connect_db("/invalid/path")
