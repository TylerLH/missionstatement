from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

from mongokit import *
import datetime

connection = Connection()

@connection.register
class Project(Document):
	structure = {
		'title':unicode,
		'short_desc':unicode,
		'twitter_desc':unicode,
		'created_at':datetime.datetime
	}
	required_fields = ['title', 'created_at']
	default_values = {'created_at':datetime.datetime.utcnow}

@app.route("/")
def hello():
    return render_template("layout.html")

if __name__ == "__main__":
    app.run()