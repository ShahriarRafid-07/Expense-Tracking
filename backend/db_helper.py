import mysql.connector
from contextlib import contextmanager
from backend.logging_setup import setup_logger

logger = setup_logger('db_helper')


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


def fetch_expenses_for_date(expense_date, user_id):
    logger.info(f"fetch_expenses_for_date: {expense_date}, user_id: {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT amount, category, notes FROM expenses WHERE expense_date=%s AND user_id=%s ORDER BY id;",
            (expense_date, user_id)
        )
        expenses = cursor.fetchall()
    return expenses

def insert_expense(expense_date, amount, category, notes, user_id):
    logger.info(f"insert_expense: {expense_date}, user_id: {user_id}, [ENCRYPTED DATA]")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes, user_id) VALUES (%s, %s, %s, %s, %s)",
            (expense_date, str(amount), category, notes, user_id)  # Store amount as string
        )


def delete_expense_for_date(expense_date, user_id):
    logger.info(f"delete_expense_for_date: {expense_date}, user_id: {user_id}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date=%s AND user_id=%s", (expense_date, user_id))


def fetch_expense_summary(start_date, end_date, user_id):
    logger.info(f"fetch_expense_summary: {start_date}, {end_date}, user_id: {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, SUM(amount) as total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s AND user_id=%s
            GROUP BY category;''', (start_date, end_date, user_id))
        data = cursor.fetchall()
        return data


def fetch_monthly_expense_summary(year, user_id):
    logger.info(f"fetch_monthly_expense_summary: {year}, user_id: {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT 
                MONTH(expense_date) as month,
                MONTHNAME(expense_date) as month_name,
                SUM(amount) as total
            FROM expenses
            WHERE YEAR(expense_date) = %s AND user_id=%s
            GROUP BY MONTH(expense_date), MONTHNAME(expense_date)
            ORDER BY MONTH(expense_date);''', (year, user_id))
        data = cursor.fetchall()
        return data


def fetch_all_expenses_with_id(user_id):
    logger.info(f"fetch_all_expenses_with_id: user_id: {user_id}")
    with get_db_cursor() as cursor:
        cursor.execute(
            """SELECT id, expense_date, amount, category, notes 
               FROM expenses 
               WHERE user_id=%s
               ORDER BY expense_date DESC, id DESC""",
            (user_id,)
        )
        expenses = cursor.fetchall()
        return expenses


def delete_expense_by_id(expense_id, user_id):
    logger.info(f"delete_expense_by_id: {expense_id}, user_id: {user_id}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE id=%s AND user_id=%s", (expense_id, user_id))


def update_expense_by_id(expense_id, amount, category, notes, user_id):
    logger.info(f"update_expense_by_id: {expense_id}, amount: {amount}, user_id: {user_id}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE expenses SET amount=%s, category=%s, notes=%s WHERE id=%s AND user_id=%s",
            (amount, category, notes, expense_id, user_id)
        )


