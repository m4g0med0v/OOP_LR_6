#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Выполнить индивидуальное задание 2 лабораторной работы 2.19, добавив
# аннотации типов. Выполнить проверку программы с помощью утилиты mypy.

import argparse
import logging
import os
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple


class ConnectError(Exception): ...


# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format=(
        "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d"
        " %(levelname)-7s - %(message)s"
    ),
)


def connect_db(db_name: str) -> sqlite3.Connection:
    """Создание соединения с базой данных и создание таблиц."""
    try:
        if not Path("data/").exists():
            os.mkdir("data")
        conn = sqlite3.connect(f"data/{db_name}.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                number TEXT NOT NULL UNIQUE,
                time TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_name TEXT NOT NULL,
                train_id INTEGER,
                FOREIGN KEY (train_id) REFERENCES trains(id)
            )
        """)

        conn.commit()
        logging.info("Соединение с базой данных успешно установлено.")
        return conn
    except Exception as e:
        logging.error("Ошибка при подключении к базе данных: %s", e)
        raise ConnectError()


def add_train(
    conn: sqlite3.Connection,
    destination: str,
    number: str,
    time: str,
    station_name: str,
) -> Optional[Tuple[str, str, str, str]]:
    """Добавить новый поезд и связанную станцию в базу данных."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO trains (destination, number, time) VALUES (?, ?, ?)",
            (destination, number, time),
        )
        train_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO stations (station_name, train_id) VALUES (?, ?)",
            (station_name, train_id),
        )

        conn.commit()
        logging.info(
            "Добавлен поезд №%s, пункт назначения: %s, время отправления: %s.",
            number,
            destination,
            time,
        )
        return find_train(conn, number)
    except sqlite3.IntegrityError:
        logging.error("Поезд с номером %s уже существует.", number)
        print(f"Ошибка: поезд с номером {number} уже существует.")
    except Exception as e:
        logging.error("Ошибка при добавлении поезда: %s", e)
        print(f"Ошибка при добавлении поезда: {e}")
    return None


def list_trains(
    conn: sqlite3.Connection,
) -> List[Tuple[str, str, str, str]]:
    """Вывести все поезда и их станции."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trains.number, trains.destination, trains.time, stations.station_name
            FROM trains
            LEFT JOIN stations ON trains.id = stations.train_id
        """)

        trains = cursor.fetchall()
        if trains:
            logging.info("Список поездов успешно извлечен.")
            return trains
        else:
            logging.info("Список поездов пуст.")
            return []
    except Exception as e:
        logging.error("Ошибка при получении списка поездов: %s", e)
        print(f"Ошибка при получении списка поездов: {e}")
    return []


def find_train(
    conn: sqlite3.Connection, number: str
) -> Optional[Tuple[str, str, str, str]]:
    """Найти и вывести информацию о поезде по его номеру."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT trains.number, trains.destination, trains.time, stations.station_name
            FROM trains
            LEFT JOIN stations ON trains.id = stations.train_id
            WHERE trains.number = ?
        """,
            (number,),
        )

        train = cursor.fetchone()
        if isinstance(train, tuple) and len(train) == 4:
            logging.info("Поиск поезда №%s завершен.", number)
            return train  # Успешный результат
        else:
            logging.info("Поезд №%s не найден.", number)
            return None
    except Exception as e:
        logging.error("Ошибка при поиске поезда №%s: %s", number, e)
        print(f"Ошибка при поиске поезда: {e}")
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Управление списком поездов")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Команды")

    add_parser = subparsers.add_parser("add", help="Добавить новый поезд")
    add_parser.add_argument(
        "-d", "--destination", required=True, help="Название пункта назначения"
    )
    add_parser.add_argument("-n", "--number", required=True, help="Номер поезда")
    add_parser.add_argument(
        "-t", "--time", required=True, help="Время отправления (чч:мм)"
    )
    add_parser.add_argument("-s", "--station", required=True, help="Название станции")

    subparsers.add_parser("list", help="Показать все поезда")

    find_parser = subparsers.add_parser("find", help="Найти поезд по номеру")
    find_parser.add_argument("number", help="Номер поезда для поиска")

    args = parser.parse_args()

    try:
        conn = connect_db("trains")

        if args.command == "add":
            ans = add_train(
                conn, args.destination, args.number, args.time, args.station
            )
            if ans:
                print(f"Поезд №{ans[0]} в {ans[1]} добавлен.")

        if args.command == "list":
            trains = list_trains(conn)
            if trains:
                for train in trains:
                    print(
                        f"Поезд №{train[0]} отправляется в {train[1]}"
                        "в {train[2]}, станция: {train[3]}."
                    )
            else:
                print("Нет данных о поездах.")

        elif args.command == "find":
            ans = find_train(conn, args.number)
            if ans:
                print(
                    f"Поезд №{ans[0]} отправляется в {ans[1]} в {ans[2]},"
                    " станция: {ans[3]}."
                )
            else:
                print(f"Поезд с номером {args.number} не найден.")

        conn.close()
    except Exception as e:
        logging.error("Необработанная ошибка: %s", e)
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
