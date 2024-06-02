from flask import Flask, render_template
import db

app = Flask(__name__)

@app.route("/")
def index():
    db.test()
    return render_template("index.html")


