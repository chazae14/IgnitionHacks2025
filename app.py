from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
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

@app.route("/page3", methods=["GET", "POST"])
def page3():
    if request.method == "POST":
        print()
    else:
        conn = sqlite3.connect('books.db')
        conn.row_factory = sqlite3.Row #makes it like a dictionary
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = [dict(row) for row in cursor.fetchall()]
        book = random.choice(books)
        return render_template("page3.html", book = book)

@app.route("/page4", methods=["GET", "POST"])
def page4():
    if request.method == "POST":
        conn = sqlite3.connect('books.db')
        conn.row_factory = sqlite3.Row #makes it like a dictionary
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id = ?",(request.form.get("book_id"),))
        book = cursor.fetchone()
        conn.close()
        return render_template("page4.html", book = dict(book))
    
@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if request.method == "POST":
        uid = session["user_id"]

        genres = request.form.getlist("genre")[:3]
        g1, g2, g3 = (genres + [None, None, None])[:3]

        b1 = request.form.get("book1") or None
        b2 = request.form.get("book2") or None
        b3 = request.form.get("book3") or None
        
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute(""" UPDATE users
                        SET genre1 = ?,
                            genre2 = ?,
                            genre3 = ?,
                            book1  = ?,
                            book2  = ?,
                            book3  = ?
                        WHERE id = ?""", 
                        (g1, g2, g3, b1, b2, b3, uid))
        conn.commit()
        conn.close()

        return redirect("/")
    
    else:
        uid = session.get("user_id")
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT genre1,genre2,genre3,book1,book2,book3 FROM users WHERE id = ?", (uid,))
        row = cur.fetchone()
        conn.close()
        
        return render_template("pref.html", row=row)
