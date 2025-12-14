from fastapi import FastAPI, HTTPException, Depends, Header
from datetime import date
from backend import db_helper, auth_helper
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()


class Expense(BaseModel):
    amount: float
    category: str
    notes: str


class DateRange(BaseModel):
    start_date: date
    end_date: date


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# Enhanced user_id extraction with validation
def get_user_id(user_id: Optional[str] = Header(None, alias="user-id")):
    """Extract and validate user_id from header"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required. Please log in.")

    try:
        user_id_int = int(user_id)
        if user_id_int <= 0:
            raise HTTPException(status_code=401, detail="Invalid user credentials.")
        return user_id_int
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")


# Public endpoints (no authentication required)
@app.post("/register")
def register(user: UserCreate):
    """Register a new user"""
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    result = auth_helper.create_user(user.username, user.password)
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@app.post("/login")
def login(user: UserLogin):
    """Authenticate user and return user credentials"""
    result = auth_helper.verify_user(user.username, user.password)
    if result["success"]:
        return {"user_id": result["user_id"], "username": result["username"]}
    else:
        raise HTTPException(status_code=401, detail=result["message"])


# Protected endpoints (require authentication)
@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date, user_id: int = Depends(get_user_id)):
    """Get expenses for a specific date - USER ISOLATED"""
    expenses = db_helper.fetch_expenses_for_date(expense_date, user_id)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense], user_id: int = Depends(get_user_id)):
    """Add or update expenses - USER ISOLATED"""
    # Delete only THIS user's expenses for this date
    db_helper.delete_expense_for_date(expense_date, user_id)

    # Insert expenses only for THIS user
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes, user_id)

    return {"message": "Expenses updated successfully"}


@app.post("/analytics/")
def get_analytics(date_range: DateRange, user_id: int = Depends(get_user_id)):
    """Get expense analytics by category - USER ISOLATED"""
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date, user_id)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database")

    if len(data) == 0:
        return {}

    total = sum([row['total'] for row in data])

    breakdown = {}
    for row in data:
        percentage = (row['total'] / total) * 100 if total != 0 else 0
        breakdown[row["category"]] = {
            "total": row['total'],
            "percentage": percentage
        }

    return breakdown


@app.post("/analytics_month/")
def get_analytics_month(year: int, user_id: int = Depends(get_user_id)):
    """Get monthly expense analytics - USER ISOLATED"""
    data = db_helper.fetch_monthly_expense_summary(year, user_id)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve monthly expense summary from the database")

    monthly_data = []
    for row in data:
        monthly_data.append({
            "month": row["month"],
            "month_name": row["month_name"],
            "total": float(row["total"])
        })

    return monthly_data


@app.get("/expenses/")
def get_all_expenses(user_id: int = Depends(get_user_id)):
    """Get all expenses for the authenticated user - USER ISOLATED"""
    expenses = db_helper.fetch_all_expenses_with_id(user_id)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, user_id: int = Depends(get_user_id)):
    """Delete a specific expense - USER ISOLATED (prevents deleting other users' expenses)"""
    db_helper.delete_expense_by_id(expense_id, user_id)
    return {"message": "Expense deleted successfully"}


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: Expense, user_id: int = Depends(get_user_id)):
    """Update a specific expense - USER ISOLATED (prevents updating other users' expenses)"""
    db_helper.update_expense_by_id(expense_id, expense.amount, expense.category, expense.notes, user_id)
    return {"message": "Expense updated successfully"}


# Health check endpoint
@app.get("/")
def root():
    """API health check"""
    return {"message": "Expense Tracker API is running", "status": "healthy"}