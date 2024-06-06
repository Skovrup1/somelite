from flask import Blueprint, render_template, redirect, url_for, request  # , flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import Db
from app import db, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    email = email.lower()

    with db.connect().cursor() as cur:
        print("USERS")
        print(Db.get_users(cur))
        user = Db.get_user_by_email(cur, email)

    if not user:
        print("no user by that email")
        return redirect(url_for("auth.login"))

    user_pass = user[3]

    password = request.form.get("password")
    print("pass")
    print(password)
    pass_match = check_password_hash(user_pass, password)

    if pass_match:
        current_user.id = user[0]
        current_user.name = user[1]

        return redirect(url_for("main.home"))
    else:
        return redirect(url_for("auth.login"))


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    name = request.form.get("name")
    name = name.lower()
    print(name)

    email = request.form.get("email")
    email = email.lower()
    print(email)

    password = request.form.get("password")
    hashed_password = generate_password_hash(password)
    print(hashed_password)

    with db.connect().cursor() as cur:
        Db.create_user(cur, name, email, hashed_password, 20)

        users = Db.get_users(cur)
        print(users)

    # if email_exists:
    #    flash('Email address already exists')
    #    return redirect(url_for("auth.signup"))

    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    return "Logout"
