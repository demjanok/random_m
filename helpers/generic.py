import sqlite3
import random
import string
import hashlib
import asyncio
from typing import LiteralString


def hash_passwd(passwd: str) -> str:
    return hashlib.sha256(passwd.encode()).hexdigest()


def generate_id(length=8) -> LiteralString:
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def create_table(filename='my_database.db'):
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    pass TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    date_posted DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # cursor.execute('CREATE INDEX idx_username ON Users (username)')
    connection.commit()
    connection.close()


