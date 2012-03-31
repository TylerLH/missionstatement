from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

from mongokit import *
import datetime, string, random

connection = Connection()

@connection.register
class Project(Document):
	structure = {
		'title':unicode,
		'identifier':unicode,
		'short_desc':unicode,
		'twitter_desc':unicode,
		'created_at':datetime.datetime
	}

	# creates a url string for the project
	def create_identifier(size=6, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for x in range(size))

	required_fields = ['title', 'created_at']
	default_values = {'created_at':datetime.datetime.utcnow, 'identifier':create_identifier()}
	indexes = [ 
		{
			'fields':['identifier'],
			'unique':True
		} 
	]

@app.route("/")
def hello():
    return render_template("layout.html")

if __name__ == "__main__":
    app.run()