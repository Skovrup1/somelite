from flask import Flask, render_template
import db

app = Flask(__name__)

@app.route("/")
def index():
    db.create()
    posts_by_user = db.get_posts_by_user()
    print(posts_by_user)
    return render_template("main.html", posts=posts_by_user)


