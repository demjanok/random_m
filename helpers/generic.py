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

if __name__ == '__main__':
    hesh = hash_passwd('admin')
    print(hesh)