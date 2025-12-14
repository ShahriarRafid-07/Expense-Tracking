import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
#from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
API_URL = os.getenv("API_URL", "http://localhost:8000")


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Derive an encryption key from user's password"""
    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100_000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def get_encryption_key(password: str, username: str) -> bytes:
    """Generate encryption key from password and username (as salt)"""
    # Use username as salt (consistent for each user)
    salt = hashlib.sha256(username.encode()).digest()[:16]
    return derive_key_from_password(password, salt)

def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt data using Fernet symmetric encryption"""
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt data using Fernet symmetric encryption"""
    try:
        f = Fernet(key)
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = f.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        return f"[DECRYPTION ERROR: {str(e)}]"

def encrypt_expense(expense: dict, key: bytes) -> dict:
    """Encrypt sensitive fields in an expense"""
    return {
        "amount": encrypt_data(str(expense["amount"]), key),
        "category": encrypt_data(expense["category"], key),
        "notes": encrypt_data(expense["notes"], key)
    }

def decrypt_expense(expense: dict, key: bytes) -> dict:
    """Decrypt sensitive fields in an expense"""
    try:
        return {
            "amount": float(decrypt_data(expense["amount"], key)),
            "category": decrypt_data(expense["category"], key),
            "notes": decrypt_data(expense["notes"], key)
        }
    except Exception as e:
        return {
            "amount": 0.0,
            "category": "[ENCRYPTED]",
            "notes": "[ENCRYPTED]"
        }

