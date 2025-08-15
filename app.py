from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mfmdfkedwlkdf'

@app.after_request
def after_request(r):
    """Stops caching"""
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = 0
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def index():
    return "Hello"

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row #makes it like a dictionary
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if len(users) != 1 or not check_password_hash(users[0]["password"], request.form.get("password")):
            return("invalid username and/or password")
        session["user_id"] = users[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        if request.form.get("password") != request.form.get("confirmpassword"):
            return "passwords don't match"
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row #makes it like a dictionary
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        users = [dict(row) for row in cursor.fetchall()]
        try:
            username = request.form.get("username")
            passwordhash = generate_password_hash(request.form.get("password"))
            cursor.execute("INSERT INTO users (username, password) VALUES(?,?)", (username, passwordhash))
            conn.commit()
            conn.close()
            return redirect("/")
        except:
            conn.close()
            return "username unavailable"
    else:
        return render_template("register.html")