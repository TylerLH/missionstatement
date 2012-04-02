from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

from flask.ext.mongokit import MongoKit, Document
import datetime, string, random
from flaskext.wtf import Form, TextField, TextAreaField, Required
app.debug = True
app.config['SECRET_KEY'] = "5A9580DAAA1C8736783C3C0968B89FEC5337AC49286E6FA4D2AFD3400FB90235"

MONGODB_DATABASE = "missionstatement_dev"
CSRF_ENABLED = True

# creates a url string for the project
def create_url(size=6, chars=string.ascii_uppercase + string.digits):
  return u''.join(random.choice(chars) for x in range(size))

# Project Model
class Project(Document):
  __collection__ = 'projects'
  structure = {
    'title':unicode,
    'unique_url':unicode,
    'short_desc':unicode,
    'twitter_desc':unicode,
    'created_at':datetime.datetime
  }

  required_fields = ['title', 'created_at', 'unique_url']
  default_values = {'created_at':datetime.datetime.utcnow, 'title':u''}
  use_dot_notation = True
  indexes = [ 
    {
      'fields':['unique_url'],
      'unique':True
    } 
  ]

db = MongoKit(app)
db.register([Project])

class ProjectForm(Form):
    title = TextField("Project Title")
    short_desc = TextField("5 Words")
    twitter_desc = TextAreaField("Twitter Description")

@app.route("/")
def hello():
    return redirect(url_for('new_project'))

@app.route("/new/")
def new_project():
    project = db.Project()
    project.unique_url = create_url()
    project.save()
    return redirect(url_for('show_project', unique_url=project['unique_url'].encode('UTF8')))

@app.route('/<unique_url>', methods=["GET", "POST"])
def show_project(unique_url):
    form = ProjectForm(request.form)
    project = db.Project.find_one({'unique_url':unique_url})
    if request.method == "POST":
        form.populate_obj(project)
        project.save()
        flash('Successfully updated Mission Statement!')
        return redirect(url_for('show_project', unique_url=unique_url))
    form = ProjectForm(obj=project)
    return render_template('new_project.html', form=form)

if __name__ == "__main__":
    app.run()