from flask import Flask, render_template, redirect, url_for, request, session
from database import get_db_conn, construct_db, drop_db
from werkzeug.security import generate_password_hash, check_password_hash

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
    form_name = request.form.get("name").strip().title()
    form_username = request.form.get("username").strip()
    form_password = request.form.get("password").strip()
    form_password_confirm = request.form.get("password-confirm").strip()

    if form_name and form_username and form_password and form_password_confirm:
        name = form_name.strip().title()
        username = form_username.strip()
        password = form_password.strip()
        password_confirm = form_password_confirm.strip()

        if password != password_confirm:
            return redirect(url_for("register") + "?err=passwords")
        else:
            conn, cur = get_db_conn()
            query = "SELECT id FROM users WHERE username = ?"
            cur.execute(query, (username,))
            row = cur.fetchone()
            if row:
                conn.close()
                return redirect(url_for("register") + "?err=username")
            else:
                password_hash = generate_password_hash(password)

                query = "INSERT INTO users (name, username, password) VALUES (?, ?, ?)"
                cur.execute(query, (name, username, password_hash))
                conn.commit()

                query = "SELECT id FROM users WHERE username = ?"
                cur.execute(query, (username,))
                row = cur.fetchone()
                conn.close()
                if row:
                    row_id = row[0]
                    session["id"] = row_id
                    return redirect(url_for("landing"))
                else:
                    return redirect(url_for("register") + "?err=login")
    else:
        return redirect(url_for("register") + "?err=input")
    return redirect(url_for("register") + "?err=unknown")


@app.route("/login")
def login():
    err = None
    err = request.args.get("err")
    return render_template("main/login.html", err=err)


@app.route("/login-input", methods=["POST"])
def login_input():
    form_username = request.form.get("username")
    form_password = request.form.get("password")

    if form_username and form_password:
        username = form_username.strip()
        password = form_password.strip()

        conn, cur = get_db_conn()
        query = "SELECT id, password FROM users WHERE username = ?"
        cur.execute(query, (username,))
        row = cur.fetchone()
        conn.close()
        if row:
            row_id = row[0]
            row_password = row[1]

            if check_password_hash(row_password, password):
                session["id"] = row_id
                return redirect(url_for("landing"))
            else:
                return redirect(url_for("login") + "?err=incorrect")
        else:
            return redirect(url_for("login") + "?err=incorrect")
    else:
        return redirect(url_for("login") + "?err=input")
    return redirect(url_for("login") + "?err=unknown")


@app.route("/create-session")
def create_sesion():
    return render_template("main/create-session.html")


@app.route("/create-session-input", methods=["POST"])
def create_session_input():
    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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