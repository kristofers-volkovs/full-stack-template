import random
import string


class RandomStrings:
    @staticmethod
    def random_string() -> str:
        return "".join(random.choices(string.ascii_lowercase, k=32))

    @classmethod
    def random_email(cls) -> str:
        return f"{cls.random_string()}@{cls.random_string()}.com"
