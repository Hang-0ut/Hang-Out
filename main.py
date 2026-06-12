from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template("main/landing.html")


@app.route("/register")
def register():
    return render_template("main/register.html")


@app.route("/register-input", methods=["POST"])
def register_input():
    return redirect(url_for("main/landing"))


@app.route("/login")
def login():
    return render_template("main/login.html")


@app.route("/login-input", methods=["POST"])
def login_input():
    return redirect(url_for("main/landing"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register-input")
def register_input():
    return redirect(url_for("/"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login-input")
def login_input():
    return redirect(url_for("/"))


if __name__ == "__main__":
    app.run()