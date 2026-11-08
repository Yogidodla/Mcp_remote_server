from fastmcp import FastMCP
import os
import json
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__),"expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__),"categories.json")
mcp = FastMCP(name="ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
            )"""
        )

init_db()

@mcp.tool
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """Add an expense to the database"""

    with sqlite3.connect(DB_PATH) as c:
        curr = c.execute(
            """INSERT INTO expenses
            (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)""",
            (date, amount, category, subcategory, note)
        )

        return {
            "status": "ok",
            "id": curr.lastrowid
        }


@mcp.tool
def list_expenses(start_date:str,end_date:str):
    '''list expenses entries within an inclusive data range'''
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        cur = c.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC",(start_date,end_date))
        return [dict(row) for row in cur.fetchall()]

@mcp.tool
def summarize(start_date:str,end_date:str,category:str=None):
    '''Summarize expenses by category within an inclusive date range'''
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        query=(
            """SELECT category,SUM(amount) as total_amount FROM expenses WHERE data BETWEEN ? AND ?"""
        )
        params = [start_date,end_date]
        if category:
            query += "AND category=?"
            params.append(category)

        query += "GROUP BY category ORDER BY category ASC"

        cur = c.execute(query,params)
        return [dict(row) for row in cur.fetchall()]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)
