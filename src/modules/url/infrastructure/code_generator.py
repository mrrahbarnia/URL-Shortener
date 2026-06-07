import string
import random

from src.core.config import ENVS

ALPHABET = string.digits + string.ascii_letters  # 0-9A-Za-z


class ICodeGenerator:
    def generate_code(self, length: int = ENVS.CONSTANT.SHORT_CODE_LENGTH) -> str:
        return "".join(random.choices(ALPHABET, k=length))

    def encode_base62(self, num: int) -> str:
        code: list[str] = []
        while num:
            code.append(ALPHABET[num % 62])
            num //= 62
        return "".join(reversed(code)).zfill(7)
