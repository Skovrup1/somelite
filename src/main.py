from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user

from database import Db
from util import Util
from app import db
from post import Post

main = Blueprint("main", __name__)


@main.route("/")
def index():
    posts = db.get_posts()
    posts = Util.convert_to_web(posts)

    return render_template("main.html", posts=posts, user=current_user)


@main.route("/home")
@login_required
def home():
    # posts = db.get_posts_by_user()
    with db.connect().cursor() as cur:
        names_posts = Db.get_names_and_posts(cur)
        new_posts = []

        for name_post in names_posts:
            (name, *post) = name_post
            new_posts.append((name, Post(*post)))

        return render_template("main.html", posts=new_posts, user=current_user)


@main.route("/friends")
@login_required
def friends():
    names_posts = db.get_posts_of_friends(current_user.id)
    new_posts = []

    for name_post in names_posts:
        (name, *post) = name_post
        new_posts.append((name, Post(*post)))

    print(friends)
    return render_template("main.html", posts=new_posts, user=current_user)


@main.route("/friends", methods=["POST"])
@login_required
def friends_post():
    post_id = request.form.get("post_id")

    db.like_post(current_user.id, post_id)

    return redirect(url_for("main.friends"))


@main.route("/groups")
@login_required
def groups():
    # posts = db.get_posts_of_groups()
    posts = db.get_posts()
    posts = Util.convert_to_web(posts)

    return render_template("main.html", posts=posts, user=current_user)
