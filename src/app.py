from flask import Flask, render_template
import db

app = Flask(__name__)


@app.route("/")
def index():
    db.create()
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@app.route("/home")
def home():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@app.route("/friends")
def friends():
    # hardcoded as alice for now
    posts = db.get_posts_of_friends(1)
    print(friends)
    return render_template("main.html", posts=posts)


@app.route("/groups")
def groups():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@app.route("/log_out")
def log_out():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)
