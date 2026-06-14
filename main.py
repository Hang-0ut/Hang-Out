from flask import Flask, render_template, redirect, url_for, request, session
from database import get_db_conn, construct_db, drop_db

app = Flask(__name__)
app.secret_key = "bguy43bf3498b8072r8"


@app.before_request
def before_reuqest():
    construct_db()


@app.route("/")
def landing():
    return render_template("main/landing.html")


@app.route("/register")
def register():
    err = None
    err = request.args.get("err")
    return render_template("main/register.html", err=err)


@app.route("/register-input", methods=["POST"])
def register_input():
    name = request.form.get("name").strip().title()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    password_confirm = request.form.get("password-confirm").strip()

    if password != password_confirm:
        return redirect(url_for("register") + "?err=passwords")
    else:
        conn, cur = get_db_conn()
        query = "SELECT id FROM users WHERE username = ?"
        cur.execute(query, (username,))
        row = cur.fetchone()
        if row:
            return redirect(url_for("register") + "?err=username")
        else:
            query = "INSERT INTO users (name, username, password) VALUES (?, ?, ?)"
            cur.execute(query, (name, username, password))
            conn.commit()

            query = "SELECT id FROM users WHERE username = ?"
            cur.execute(query, (username,))
            row = cur.fetchone()
            if row:
                id = row[0]
                session["id"] = id
                return redirect(url_for("landing"))
            else:
                return redirect(url_for("register") + "?err=login")
    return redirect(url_for("register") + "?err=unknown")


@app.route("/login")
def login():
    return render_template("main/login.html")


@app.route("/login-input", methods=["POST"])
def login_input():
    return redirect(url_for("landing"))


# admin routes


@app.route("/admin/", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "drop_db":
            drop_db()
        elif action == "build_db":
            return "not yet implemented"
        elif action == "drop_rebuild_db":
            return "not yet implemented"
    return render_template("admin/main.html")


@app.route("/admin/query", methods=["GET", "POST"])
def query():
    query = "SELECT * FROM users ORDER BY id"

    if request.method == "POST":
        query = request.form.get("query")

    conn, cur = get_db_conn()

    data = []
    columns = []

    err = "none"

    try:
        cur.execute(query)
        data = cur.fetchall()

        if cur.description:
            columns = [desc[0] for desc in cur.description]

    except Exception as e:
        err = f"SQL Error: ({e}) Please report to developer"

    conn.commit()
    conn.close()

    return render_template(
        "admin/query.html",
        query=query,
        data=data,
        columns=columns,
        err = err
    )


if __name__ == "__main__":
    app.run()