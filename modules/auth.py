from flask import Blueprint, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_routes = Blueprint("auth_routes", __name__)

DATABASE = "database/app.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


@auth_routes.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (username, email, password, datetime.now()),
            )
            conn.commit()
        except:
            return "Email already exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")


@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, password_hash FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")


@auth_routes.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/login")