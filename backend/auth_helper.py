import hashlib
import mysql.connector
from contextlib import contextmanager
from backend.logging_setup import setup_logger

logger = setup_logger('auth_helper')


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="iLy30@stm",  # Update with your password
        database="expense_manager"
    )
    cursor = connection.cursor(dictionary=True)
    yield cursor

    if commit:
        connection.commit()

    cursor.close()
    connection.close()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, password):
    """Create a new user"""
    logger.info(f"create_user: {username}")
    password_hash = hash_password(password)

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            return {"success": True, "message": "User created successfully"}
    except mysql.connector.IntegrityError:
        return {"success": False, "message": "Username already exists"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return {"success": False, "message": "Failed to create user"}


def verify_user(username, password):
    """Verify user credentials"""
    logger.info(f"verify_user: {username}")
    password_hash = hash_password(password)

    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id, username FROM users WHERE username=%s AND password_hash=%s",
            (username, password_hash)
        )
        user = cursor.fetchone()

        if user:
            return {"success": True, "user_id": user["id"], "username": user["username"]}
        else:
            return {"success": False, "message": "Invalid username or password"}