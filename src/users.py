import hashlib
from uuid import UUID, uuid4

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

import constants


cursor: MySQLCursor | None = None
db: MySQLConnection | None = None


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
        "   uuid CHAR(36) PRIMARY KEY,"
        "   username VARCHAR(255),"
        "   password_hash VARCHAR(255),"
        "   last_logoff_location_x FLOAT,"
        "   last_logoff_location_y FLOAT"
        ")"
    )

    return cursor


def check_login(username: str, password: str) -> tuple[UUID, float, float] | None:
    # TODO protect from sql injection
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    sql = "SELECT uuid," \
          "       last_logoff_location_x," \
          "       last_logoff_location_y FROM users where username = %s AND password_hash = %s"
    val = (username, password_hash)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if not result:
        return None
    return UUID(result[0]), result[1], result[2]


def register(username: str, password: str) -> None | UUID:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    register_sql = "INSERT INTO users (" \
                   "    uuid," \
                   "    username," \
                   "    password_hash," \
                   "    last_logoff_location_x," \
                   "    last_logoff_location_y)" \
                   "VALUES (%s, %s, %s, %s, %s)"
    check_username_sql = "SELECT * FROM users where username = %s"
    check_username_val = (username,)
    uuid = uuid4()
    register_val = (str(uuid), username, password_hash, -1, -1)
    cursor.execute(check_username_sql, check_username_val)
    existing_user = cursor.fetchone()
    if existing_user:
        return None
    else:
        cursor.execute(register_sql, register_val)
        db.commit()
        return uuid


def set_last_logoff_location(uuid: UUID, x: float, y: float):
    sql = "UPDATE users SET last_logoff_location_x = %s, last_logoff_location_y = %s WHERE uuid = %s"
    val = (x, y, str(uuid))
    cursor.execute(sql, val)
    db.commit()

