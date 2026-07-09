import bcrypt
import hashlib
import base64


def _pre_hash_password(password: str) -> bytes:
    """Внутренняя функция для предварительного хеширования."""
    sha_hashed = hashlib.sha256(password.encode()).digest()
    return base64.b64encode(sha_hashed)


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt + SHA-256."""
    password_for_bcrypt = _pre_hash_password(password)
    hashed = bcrypt.hashpw(password_for_bcrypt, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""

    password_for_bcrypt = _pre_hash_password(plain_password)
    return bcrypt.checkpw(
        password_for_bcrypt,
        hashed_password.encode('utf-8')
    )
