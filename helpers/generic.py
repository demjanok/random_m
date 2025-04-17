import random
import string
import hashlib
import re

from typing import LiteralString
from unidecode import unidecode


def hash_passwd(passwd: str) -> str:
    return hashlib.sha256(passwd.encode()).hexdigest()


def generate_id(length=8) -> LiteralString:
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def transliterate_to_snake(text):
    text = unidecode(text)
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    words = text.lower().split()
    return '_'.join(words)

# if __name__ == '__main__':
#    print(hash_passwd(''))