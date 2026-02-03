from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    password TEXT NOT NULL DEFAULT ''
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
    conn.commit()
    conn.close()

@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"}), 200

# URL: http://127.0.0.1:5000/api/register
@app.post("/api/register")
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully"}), 201

# URL: http://127.0.0.1:5000/api/users
@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = []
    for row in rows:
        user = {"id": row["id"], "name": row["name"], "email": row["email"], "password": row["password"]}
        users.append(user)
    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200

# URL: http://127.0.0.1:5000/api/users/<user_id>
@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    conn.close()
    return jsonify({
        "success": True,
        "message": "User retrieved successfully",
        "data": {"id": row["id"], "name": row["name"], "email": row["email"], "password": row["password"]}
    }), 200

# URL: http://127.0.0.1:5000/api/users/<user_id>
@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200

# URL: http://127.0.0.1:5000/api/users/<user_id>
@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?", (name, email, password, user_id))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200

# URL: http://127.0.0.1:5000/api/expenses
@app.post("/api/expenses")
def add_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, amount, date, category, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added successfully"}), 201

# Add 5 sample expenses (force clear and insert)
def seed_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")
    sample_expenses = [
        ("Groceries", "Weekly grocery shopping", 75.50, "2026-02-01", "Food", 1),
        ("Bus Pass", "Monthly bus pass", 40.00, "2026-02-01", "Transport", 1),
        ("Internet", "Monthly internet bill", 60.00, "2026-02-01", "Utilities", 2),
        ("Coffee", "Coffee with friends", 12.00, "2026-02-02", "Food", 3),
        ("Book", "Bought a programming book", 30.00, "2026-02-02", "Education", 2)
    ]
    cursor.executemany(
        "INSERT INTO expenses (title, description, amount, date, category, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        sample_expenses
    )
    conn.commit()
    conn.close()

# Call seed_expenses after init_db
if __name__ == "__main__":
    init_db()
    seed_expenses()
    app.run(debug=True)

