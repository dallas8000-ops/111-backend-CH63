from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)  # opens a connection to the database
    cursor = conn.cursor()           # Creates a cursor/tool that lets us send commands

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit() #save to the database
    conn.close()# close the connection

@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"}), 200

@app.post("/api/register")
def register():
    data = request.get_json() #retieve the data from the user
    print(data)
    user = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not user or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (user, email, password))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)