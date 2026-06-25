from flask import Flask, render_template, redirect, url_for, request, session
from database import get_db_conn, construct_db, drop_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "bguy43bf3498b8072r8"


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get("id"):
            return redirect("/login")
        return func(*args, **kwargs)

    return decorated_view


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


def get_friends_of(user_id, conn, cur):
    query = "SELECT friends FROM users WHERE id = ?"
    cur.execute(query, (user_id,))
    row = cur.fetchone()
    friends_ids_str = row[0]
    if friends_ids_str:
        friends_id_list = friends_ids_str.split(",")
        placeholders = ",".join(["?"] * len(friends_id_list))
        query = f"SELECT id, name, username FROM users WHERE id IN ({placeholders})"
        cur.execute(query, friends_id_list)
        friends = cur.fetchall()
    else:
        friends = []
    
    return friends


@login_required
@app.route("/friends", methods=["GET", "POST"])
def friends():
    user_id = session.get("id")
    conn, cur = get_db_conn()
    username = ""

    if request.method == "POST":
        username = request.form.get("username")
        like_username = f"%{username}%"
        query = "SELECT id, username FROM users WHERE username LIKE ? AND id != ?"
        cur.execute(query, (like_username, user_id))
        search_results = cur.fetchall()

        action = request.form.get("action")
        if action != "none":
            action, friend_id = action.split("-")
            friends = get_friends_of(user_id, conn, cur)
            if action == "remove":
                if friend_id in friends:
                    friends.remove(friend_id)
            elif action == "add":
                friends.append(friend_id)
            friends_str = ",".join(friends)
            query = "UPDATE users SET friends = ? WHERE id = ?"
            cur.execute(query, (friends_str, user_id))
            conn.commit()
    else:
        search_results = "none"

    friends = get_friends_of(user_id, conn, cur)
    conn.close()
    return render_template("main/friends.html", friends=friends, search_results=search_results, username=username)


@login_required
@app.route("/create-group")
def create_group():
    return render_template("main/create-group.html")


@login_required
@app.route("/create-group-input", methods=["POST"])
def create_group_input():
    return redirect(url_for("friends"))


@login_required
@app.route("/create-session")
def create_sesion():
    return render_template("main/create-session.html")


@login_required
@app.route("/create-session-input", methods=["POST"])
def create_session_input():
    return redirect(url_for("landing"))


@login_required
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