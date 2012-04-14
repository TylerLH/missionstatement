import logging

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

from flask.ext.mongokit import MongoKit, Document
import datetime, string, random
from flaskext.wtf import Form, TextField, TextAreaField
from wtforms import ValidationError

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
                 'unique_url'  :unicode,
                 
                 'title'       :unicode,
                 'tagline'      :unicode,
                 'tweet'  :unicode,
                 'blurb'   :unicode,
                  
                 'twitter_desc':unicode,
                 'facebook_desc':unicode,
                 
                 'created_at':datetime.datetime
                 }              

    required_fields = ['title', 'tagline', 'created_at', 'unique_url']
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

def length(max=-1, words = True):  
    if words: 
        message = 'must be %d words or less.' % max
    else:
        message = 'must be %d characters long or less.' % max

    def _length(form, field):
        if words: 
            l = field.data and len(field.data.split()) or 0
        else: 
            l = field.data and len(field.data) or 0
            
        if max != -1 and l > max:
            raise ValidationError(field.label.text + " " + message)

    return _length

def required():
    def _required(form, field):
        if len(field.data) == 0:
            raise ValidationError(field.label.text + " is required.")

    return _required

def get_errors(form):
    err = ''
    for v in form.errors.values():
        err = v[0] + ' ' + err
    
    return err

class ProjectForm(Form):
    title = TextField("Title", [required(), length(max = 50, words = False)])
    tagline = TextField("Tagline", [required(), length(max = 10)])
    tweet = TextAreaField("One Tweetful", [length(max = 12, words = False)])    
    blurb = TextAreaField("Longer Email Blurb", [length(max = 500)])
    
    twitter_desc = TextAreaField("Twitter Description")
    facebook_desc = TextAreaField("Facebook Description")

@app.route("/", methods=["GET", "POST"])
def hello():
    form = ProjectForm(request.form)
    project = db.Project()
    
    if request.method == "POST": 
        if form.validate():
            form.populate_obj(project)
            project.unique_url = create_url()
            project.save()
        
            if not 'pitches' in session:
                session['pitches'] = []
            
            session['pitches'].append({'name' : project.title, 'url' : project.unique_url})
            session.modified = True
        
            flash('Saved!', category = 'success')
            return redirect(url_for('show_project', unique_url=project.unique_url))
        else:
            flash(get_errors(form), category = 'error')
            
    form = ProjectForm(obj=project)
    return render_template('new_project.html', form=form, update = False)

@app.route('/<unique_url>', methods=["GET", "POST"])
def show_project(unique_url):
    form = ProjectForm(request.form)
    project = db.Project.find_one({'unique_url':unique_url})
    
    if request.method == "POST":
        if form.validate():
            form.populate_obj(project)
            project.save()
            flash('Updated!', category = 'success')
            return redirect(url_for('show_project', unique_url=unique_url))
        else: 
            flash(get_errors(form), category = 'error')
            
    form = ProjectForm(obj=project)
    return render_template('new_project.html', form=form, update = True)

if __name__ == "__main__":
    app.run()