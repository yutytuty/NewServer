import hashlib

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from mysql.connector.cursor_cext import CMySQLCursor

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
        "   id INT AUTO_INCREMENT PRIMARY KEY,"
        "   username VARCHAR(255),"
        "   password_hash VARCHAR(255)"
        ")"
    )

    return cursor


def check_login(username: str, password: str) -> bool:
    # TODO protect from sql injection
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    sql = "SELECT * FROM users where username = %s AND password_hash = %s"
    val = (username, password_hash)

    cursor.execute(sql, val)

    if cursor.fetchone():
        return True
    return False


def register(username: str, password: str) -> bool:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    register_sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
    check_username_sql = "SELECT * FROM users where username = %s"
    check_username_val = (username,)
    register_val = (username, password_hash)
    cursor.execute(check_username_sql, check_username_val)
    existing_user = cursor.fetchone()
    if existing_user:
        return False
    else:
        cursor.execute(register_sql, register_val)
        db.commit()
        return True
