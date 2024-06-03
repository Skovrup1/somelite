from flask import Blueprint, render_template
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@main_bp.route("/home")
def home():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@main_bp.route("/friends")
def friends():
    # hardcoded as alice for now
    posts = db.get_posts_of_friends(1)
    print(friends)
    return render_template("main.html", posts=posts)


@main_bp.route("/groups")
def groups():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@main_bp.route("/logout")
def logout():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)

@main_bp.route("/login")
def login():
    return render_template("log.html")
