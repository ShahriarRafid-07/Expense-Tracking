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


# Simple user_id extraction from header
def get_user_id(user_id: Optional[str] = Header(None)):
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return int(user_id)


@app.post("/register")
def register(user: UserCreate):
    result = auth_helper.create_user(user.username, user.password)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@app.post("/login")
def login(user: UserLogin):
    result = auth_helper.verify_user(user.username, user.password)
    if result["success"]:
        return {"user_id": result["user_id"], "username": result["username"]}
    else:
        raise HTTPException(status_code=401, detail=result["message"])


@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date, user_id: int = Depends(get_user_id)):
    expenses = db_helper.fetch_expenses_for_date(expense_date, user_id)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense], user_id: int = Depends(get_user_id)):
    db_helper.delete_expense_for_date(expense_date, user_id)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes, user_id)
    return {"message": "Expenses updated successfully"}


@app.post("/analytics/")
def get_analytics(date_range: DateRange, user_id: int = Depends(get_user_id)):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date, user_id)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database")

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


@app.get("/expenses/", response_model=List[dict])
def get_all_expenses(user_id: int = Depends(get_user_id)):
    expenses = db_helper.fetch_all_expenses_with_id(user_id)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, user_id: int = Depends(get_user_id)):
    db_helper.delete_expense_by_id(expense_id, user_id)
    return {"message": "Expense deleted successfully"}


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: Expense, user_id: int = Depends(get_user_id)):
    db_helper.update_expense_by_id(expense_id, expense.amount, expense.category, expense.notes, user_id)
    return {"message": "Expense updated successfully"}