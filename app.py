from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secure123"

# ---------------- PATHS ----------------

UPLOAD = "static/uploads"
FACE = "static/faces"

VOTER_UPLOAD = os.path.join(UPLOAD, "voters")
CAND_UPLOAD = os.path.join(UPLOAD, "candidates")
VIDEO = os.path.join(UPLOAD, "videos")

# Create folders if not exist
for path in [UPLOAD, FACE, VOTER_UPLOAD, CAND_UPLOAD, VIDEO]:
    os.makedirs(path, exist_ok=True)

# ---------------- DATABASE ----------------

def db():
    return sqlite3.connect("database.db")

def init():
    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            address TEXT,
            photo TEXT,
            voted INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT
        )
    """)

    con.commit()
    con.close()

init()

# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Admin login
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        con = db()
        cur = con.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        con.close()

        if user:
            if user[6] == 1:
                flash("Already voted!")
                return redirect("/")
            
            session["user"] = username
            return redirect("/dashboard")

        flash("User not registered")

    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login_alias():
    return login()

# ---------------- ROLE SELECT ----------------

@app.route("/choose")
def choose():
    return render_template("choose_role.html")

# ---------------- REGISTER ----------------

@app.route("/register/<role>", methods=["GET", "POST"])
def register(role):

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        address = request.form["address"]

        photo = request.files["photo"]

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
        else:
            filename = "default.png"

        if role == "voter":
            photo.save(os.path.join(VOTER_UPLOAD, filename))
        else:
            photo.save(os.path.join(CAND_UPLOAD, filename))

        con = db()
        cur = con.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username,password,role,address,photo) VALUES(?,?,?,?,?)",
                (username, password, role, address, filename)
            )
            con.commit()
            flash("Registration Successful")

        except sqlite3.IntegrityError:
            flash("Username already exists")

        con.close()

        return redirect("/")

    if role == "voter":
        return render_template("voter_register.html")
    else:
        return render_template("candidate_register.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        (session["user"],)
    )

    me = cur.fetchone()

    if not me:
        con.close()
        return redirect("/")

    # Already voted check
    if me[6] == 1:
        con.close()
        flash("Already voted!")
        return redirect("/logout")

    # Get candidates
    candidates = cur.execute(
        "SELECT id, username, photo FROM users WHERE role='candidate'"
    ).fetchall()

    # Voting
    if request.method == "POST":

        vote = request.form["vote"]

        cur.execute(
            "INSERT INTO votes(candidate) VALUES(?)",
            (vote,)
        )

        cur.execute(
            "UPDATE users SET voted=1 WHERE username=?",
            (session["user"],)
        )

        con.commit()
        con.close()

        flash("Vote Successful!")
        return redirect("/dashboard")

    con.close()

    return render_template(
        "dashboard.html",
        me=me,
        candidates=candidates
    )

# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/")

    con = db()
    cur = con.cursor()

    users = cur.execute(
        "SELECT * FROM users"
    ).fetchall()

    votes = cur.execute(
        "SELECT candidate, COUNT(*) FROM votes GROUP BY candidate"
    ).fetchall()

    con.close()

    return render_template(
        "admin.html",
        users=users,
        votes=votes
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)