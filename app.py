from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
#from dotenv import load_dotenv
#load_dotenv()
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "notes_app_local_dev_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "notes.db")

def run(sql, params=(), one=False, many=False, commit=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    try:
        sql = sql.replace("%s", "?")
        cur.execute(sql, params)

        if commit:
            conn.commit()
            return cur.rowcount

        if one:
            row = cur.fetchone()
            return dict(row) if row else None

        if many:
            return [dict(row) for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return redirect(url_for("viewall" if "user_id" in session else "login"))


# ---------- User module ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        if not (username and email and password):
            flash("All fields are required.", "danger")
        elif run("SELECT id FROM users WHERE username=%s", (username,), one=True):
            flash("Username already taken.", "danger")
        else:
            run("INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
                (username, email, password), commit=True)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = run("SELECT * FROM users WHERE username=%s AND password=%s",
                   (request.form["username"].strip(), request.form["password"]), one=True)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("viewall"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        new_password = request.form["new_password"]
        user = run("SELECT id FROM users WHERE username=%s AND email=%s",
                   (username, email), one=True)
        if user and new_password:
            run("UPDATE users SET password=%s WHERE id=%s",
                (new_password, user["id"]), commit=True)
            flash("Password updated. Please log in.", "success")
            return redirect(url_for("login"))
        flash("Username and email do not match.", "danger")
    return render_template("forgot.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------- Notes module (CRUD) ----------
@app.route("/addnote", methods=["GET", "POST"])
@login_required
def addnote():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        if not title:
            flash("Title is required.", "danger")
        else:
            run("INSERT INTO notes (title, content, user_id) VALUES (%s,%s,%s)",
                (title, content, session["user_id"]), commit=True)
            flash("Note added successfully!", "success")
            return redirect(url_for("viewall"))
    return render_template("addnote.html")


@app.route("/viewall")
@login_required
def viewall():
    notes = run("SELECT * FROM notes WHERE user_id=%s ORDER BY created_at DESC",
                (session["user_id"],), many=True)
    return render_template("viewall.html", notes=notes)


def get_own_note(note_id):
    return run("SELECT * FROM notes WHERE id=%s AND user_id=%s",
               (note_id, session["user_id"]), one=True)


@app.route("/viewnotes/<int:note_id>")
@login_required
def viewnotes(note_id):
    note = get_own_note(note_id)
    if not note:
        flash("Note not found.", "danger")
        return redirect(url_for("viewall"))
    return render_template("viewnote.html", note=note)


@app.route("/updatenote/<int:note_id>", methods=["GET", "POST"])
@login_required
def updatenote(note_id):
    note = get_own_note(note_id)
    if not note:
        flash("Note not found.", "danger")
        return redirect(url_for("viewall"))
    if request.method == "POST":
        run("UPDATE notes SET title=%s, content=%s WHERE id=%s AND user_id=%s",
            (request.form["title"].strip(), request.form["content"].strip(),
             note_id, session["user_id"]), commit=True)
        flash("Note updated successfully!", "success")
        return redirect(url_for("viewall"))
    return render_template("updatenote.html", note=note)


@app.route("/deletenote/<int:note_id>", methods=["POST"])
@login_required
def deletenote(note_id):
    run("DELETE FROM notes WHERE id=%s AND user_id=%s",
        (note_id, session["user_id"]), commit=True)
    flash("Note deleted.", "info")
    return redirect(url_for("viewall"))


if __name__ == "__main__":
    app.run(debug=True)