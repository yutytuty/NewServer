import hashlib
from threading import Lock
from uuid import UUID, uuid4

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

import constants


class UserAlreadyLoggedInError(Exception):
    pass


cursor: MySQLCursor | None = None
db: MySQLConnection | None = None
cursor_lock = Lock()


def init():
    global cursor
    global db

    with open(constants.DB_PASSWORD_FILE_PATH, "r") as f:
        password = f.read()

    db = mysql.connector.connect(
        host=constants.DB_HOST,
        user=constants.DB_USER,
        password=password,
        database="game"
    )

    cursor = db.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "    uuid CHAR(36) PRIMARY KEY,"
        "    username VARCHAR(255),"
        "    password_hash VARCHAR(255),"
        "    last_logoff_location_x FLOAT DEFAULT -1,"
        "    last_logoff_location_y FLOAT DEFAULT -1,"
        "    coin_amount INT DEFAULT 0,"
        "    xp_amount INT DEFAULT 0,"
        "    is_locked BOOLEAN DEFAULT 0"
        ")"
    )

    cursor.execute("UPDATE users SET is_locked = 0")
    db.commit()


def check_login(username: str, password: str) -> tuple[UUID, float, float] | None:
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    sql = "SELECT uuid," \
          "       last_logoff_location_x," \
          "       last_logoff_location_y," \
          "       is_locked FROM users where username = %s AND password_hash = %s"
    val = (username, password_hash)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if not result:
        cursor_lock.release()
        return None
    if result[3]:
        cursor_lock.release()
        raise UserAlreadyLoggedInError(f"User with uuid {UUID(result[0])} already logged in")
    cursor_lock.release()
    return UUID(result[0]), result[1], result[2]


def register(username: str, password: str) -> None | UUID:
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    register_sql = "INSERT INTO users (uuid, username, password_hash) VALUES (%s, %s, %s)"
    check_username_sql = "SELECT * FROM users where username = %s"
    check_username_val = (username,)
    uuid = uuid4()
    register_val = (str(uuid), username, password_hash)
    cursor.execute(check_username_sql, check_username_val)
    existing_user = cursor.fetchone()
    if existing_user:
        cursor_lock.release()
        return None
    else:
        cursor.execute(register_sql, register_val)
        db.commit()
        cursor_lock.release()
        return uuid


def set_last_logoff_location(uuid: UUID, x: float, y: float):
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    sql = "UPDATE users SET last_logoff_location_x = %s, last_logoff_location_y = %s WHERE uuid = %s"
    val = (x, y, str(uuid))
    cursor.execute(sql, val)
    db.commit()
    cursor_lock.release()


def get_coin_amount(uuid: UUID) -> int:
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    sql = "SELECT coin_amount FROM users WHERE uuid = %s"
    val = (str(uuid),)
    cursor.execute(sql, val)
    amount = cursor.fetchone()[0]
    cursor_lock.release()
    return amount


def set_coin_amount(uuid: UUID, amount: int):
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    sql = "UPDATE users SET coin_amount = %s WHERE uuid = %s"
    val = (amount, str(uuid))
    cursor.execute(sql, val)
    db.commit()
    cursor_lock.release()


def get_xp_amount(uuid: UUID) -> int:
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    sql = "SELECT xp_amount FROM users WHERE uuid = %s"
    val = (str(uuid),)
    cursor.execute(sql, val)
    amount = cursor.fetchone()[0]
    cursor_lock.release()
    return amount


def set_xp_amount(uuid: UUID, amount: int):
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    sql = "UPDATE users SET xp_amount = %s WHERE uuid = %s"
    val = (amount, str(uuid))
    cursor.execute(sql, val)
    db.commit()
    cursor_lock.release()


def set_lock_for_user(uuid: UUID, val: bool):
    global cursor_lock
    cursor_lock.acquire(blocking=True)
    sql = "UPDATE users SET is_locked = %s WHERE uuid = %s"
    values = (val, str(uuid))
    cursor.execute(sql, values)
    db.commit()
    cursor_lock.release()
