from flask import Flask, render_template, redirect, url_for, request
from database import get_db_conn, construct_db, drop_db

app = Flask(__name__)


@app.before_request
def before_reuqest():
    construct_db()


@app.route("/")
def landing():
    return render_template("main/landing.html")


@app.route("/register")
def register():
    return render_template("main/register.html")


@app.route("/register-input", methods=["POST"])
def register_input():
    return redirect(url_for("landing"))


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