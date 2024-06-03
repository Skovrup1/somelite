from flask import Flask, render_template
import db

app = Flask(__name__)

@app.route("/")
def index():
    db.create()
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


