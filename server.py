# 111-backend Flask Server
# Author: Your Name
# Date: 2026-02-07

from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DB_NAME = "budget_manager.db"

print("Using database at:", os.path.abspath(DB_NAME))

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

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/api/register", methods=["POST"])
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

@app.route("/api/users", methods=["GET"])
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
    return jsonify({"success": True, "message": "Users retrieved successfully", "data": users}), 200

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({"success": True, "message": "User retrieved successfully", "data": dict(row)}), 200

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "User deleted successfully"}), 200

@app.route("/api/users/<int:user_id>", methods=["PUT"])
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
    return jsonify({"success": True, "message": "User updated successfully"}), 200

@app.route("/api/expenses", methods=["POST"])
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
    return jsonify({"success": True, "message": "Expense added successfully"}), 201

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, amount, date, category, user_id FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    expenses = []
    for row in rows:
        expense = dict(row)
        expenses.append(expense)
    return jsonify({"success": True, "message": "Expenses retrieved successfully", "data": expenses}), 200

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def get_expense_by_id(expense_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "message": "Expense not found"}), 404
    return jsonify({"success": True, "message": "Expense retrieved successfully", "data": dict(row)}), 200

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Expense not found"}), 404
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Expense deleted successfully"}), 200

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Expense not found"}), 404
    cursor.execute("""
        UPDATE expenses SET title = ?, description = ?, amount = ?, date = ?, category = ?, user_id = ?
        WHERE id = ?
    """, (title, description, amount, date, category, user_id, expense_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Expense updated successfully"}), 200

# Frontend routes
@app.route("/")
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        name = user_row['name'] if user_row else 'User'
        hobbies = ["Coding!", "Basketball"]
        cursor.execute("SELECT description, amount FROM expenses WHERE user_id = ?", (user_id,))
        expenses = [dict(description=row['description'], amount=row['amount']) for row in cursor.fetchall()]
        conn.close()
        return render_template("home.html", name=name, hobbies=hobbies, expenses=expenses)
    else:
        name = "Luis Renteria"
        hobbies = ["Coding!", "Basketball"]
        return render_template("home.html", name=name, hobbies=hobbies)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE name = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home') )

@app.route("/about")
def about():
    name = "Luis Renteria"
    hobbies = ["Coding!", "Basketball", "Listening to music", "Do nothing", "Read"]
    return render_template("about.html", name=name, hobbies=hobbies)

@app.route("/contact_me", methods=["GET", "POST"])
def contact():
    contact_info = {
        "email": "your.email@example.com",
        "phone": "+1 889-327-1234",
        "address": "123 main street, san diego, CA"
    }
    return render_template("contact_me.html", contact_info=contact_info)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

