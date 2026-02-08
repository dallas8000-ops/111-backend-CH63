import sqlite3

DB_NAME = "budget_manager.db"

# List of user IDs from your users table
user_ids = [1, 2, 4, 6, 7]

# Sample expenses for each user
expenses = [
    {"title": "Groceries", "description": "Weekly groceries", "amount": 50.25, "date": "2026-02-07", "category": "Food"},
    {"title": "Utilities", "description": "Monthly electricity bill", "amount": 120.00, "date": "2026-02-07", "category": "Bills"}
]

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for user_id in user_ids:
    for expense in expenses:
        cursor.execute("""
            INSERT INTO expenses (title, description, amount, date, category, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (expense["title"], expense["description"], expense["amount"], expense["date"], expense["category"], user_id))

conn.commit()
conn.close()
print("Added 2 expenses for each user.")
