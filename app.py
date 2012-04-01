from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

from mongokit import *
import datetime, string, random
from flaskext.wtf import Form, TextField, Required
app.debug = True
app.config['SECRET_KEY'] = "5A9580DAAA1C8736783C3C0968B89FEC5337AC49286E6FA4D2AFD3400FB90235"

db = Connection()

# Project Model
@db.register
class Project(Document):
  __collection__ = 'projects'
  __database__ = 'missionstatement_dev'
  structure = {
    'title':unicode,
    'unique_url':unicode,
    'short_desc':unicode,
    'twitter_desc':unicode,
    'created_at':datetime.datetime
  }

  # creates a url string for the project
  def create_url(size=6, chars=string.ascii_uppercase + string.digits):
    return u''.join(random.choice(chars) for x in range(size))

  required_fields = ['title', 'created_at']
  default_values = {'created_at':datetime.datetime.utcnow, 'title':u'', 'unique_url':create_url()}
  indexes = [ 
    {
      'fields':['unique_url'],
      'unique':True
    } 
  ]

class ProjectForm(Form):
  title = TextField("Project Title")

# User Model
@db.register
class User(Document):
  __collection__ = 'users'
  __database__ = 'missionstatement_dev'
  structure = {
    'username':unicode,
    'email':unicode,
    'password':unicode,
    'password_salt':unicode,
    'created_at':datetime.datetime
  }

@app.route("/")
def hello():
    return render_template("layout.html")

@app.route("/new/")
def new_project():
    project = db.Project()
    project.save()
    form = ProjectForm()
    return redirect(url_for('show_project', unique_url=project['unique_url'].encode('UTF8')))

@app.route('/p/<unique_url>')
def show_project(unique_url):
  project = db.Project.one({'unique_url':unique_url})
  return project['unique_url']

if __name__ == "__main__":
    app.run()