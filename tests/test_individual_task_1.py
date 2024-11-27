import pytest

from src.individual_task_1 import (
    ConnectError,
    add_train,
    connect_db,
    find_train,
    list_trains,
)


class TestTrainManagment:
    def test_connect_db(self, setup_db):
        """Тест успешного подключения к базе данных."""
        conn = setup_db
        assert conn, "Соединение должно быть установлено."

    def test_add_train_success(self, setup_db):
        """Тест добавления нового поезда."""
        conn = setup_db
        result = add_train(conn, "Москва", "001A", "10:00", "Киевский вокзал")
        assert result is not None, "Поезд должен быть успешно добавлен."
        assert result[0] == "001A", "Номер поезда должен совпадать."

    def test_add_train_duplicate(self, setup_db):
        """Тест добавления поезда с дублирующимся номером."""
        conn = setup_db
        add_train(conn, "Москва", "001A", "10:00", "Киевский вокзал")
        result = add_train(
            conn, "Петербург", "001A", "12:00", "Ладожский вокзал"
        )
        assert (
            result is None
        ), "Добавление дублирующего поезда должно вернуть None."

    def test_find_train_success(self, setup_db):
        """Тест успешного поиска поезда по номеру."""
        conn = setup_db
        add_train(conn, "Москва", "001A", "10:00", "Киевский вокзал")
        result = find_train(conn, "001A")
        assert result is not None, "Поезд должен быть найден."
        assert result[1] == "Москва", "Пункт назначения должен совпадать."

    def test_find_train_not_found(self, setup_db):
        """Тест поиска несуществующего поезда."""
        conn = setup_db
        result = find_train(conn, "002B")
        assert result is None, "Поезд с данным номером не должен быть найден."

    def test_list_trains(self, setup_db):
        """Тест получения списка поездов."""
        conn = setup_db
        add_train(conn, "Москва", "001A", "10:00", "Киевский вокзал")
        add_train(conn, "Петербург", "002B", "12:00", "Ладожский вокзал")
        result = list_trains(conn)
        assert len(result) == 2, "Список должен содержать два поезда."
        assert result[0][0] == "001A", "Номер первого поезда должен совпадать."
        assert (
            result[1][1] == "Петербург"
        ), "Пункт назначения второго поезда должен совпадать."

    def test_connect_db_error(self):
        """Тест обработки ошибок при подключении к базе данных."""
        with pytest.raises(ConnectError):
            connect_db("/invalid/path")
