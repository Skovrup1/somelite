from flask import Flask, render_template
import db

app = Flask(__name__)

@app.route("/")
def index():
    users = db.get_users()
    return render_template("main.html", user=users)


