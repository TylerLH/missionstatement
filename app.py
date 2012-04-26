import os
from datetime import timedelta

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

from flask.ext.mongokit import MongoKit, Document
import datetime, string, random
from flaskext.wtf import Form, TextField, TextAreaField
from wtforms import ValidationError
from flaskext.mail import Mail, Message

app.debug = True
app.config['SECRET_KEY'] = "5A9580DAAA1C8736783C3C0968B89FEC5337AC49286E6FA4D2AFD3400FB90235"
app.permanent_session_lifetime = timedelta(days = 365)

if os.environ.get('MONGOHQ_URL'):
    app.debug = False
    app.config['MONGODB_HOST'] = os.environ.get('MONGOHQ_URL')
    app.config['MONGODB_DATABASE'] = 'app4005374'

CSRF_ENABLED = True

app.config.update(
                  #EMAIL SETTINGS
                  MAIL_SERVER = 'smtp.sendgrid.net',
                  MAIL_PORT = 587,
                  MAIL_USE_SSL = True,
                  MAIL_DEBUG = app.debug,
                  MAIL_USERNAME = os.environ.get('SENDGRID_USERNAME'),
                  MAIL_PASSWORD = os.environ.get('SENDGRID_PASSWORD'),
                  )
mail = Mail(app)

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
    blurb = TextAreaField("Email Blurb / Elevator Pitch", [length(max = 500)])
    
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
                session.permanent = True
            
            session['pitches'].append({'name' : project.title, 'url' : project.unique_url})
            session.modified = True
        
            flash('Saved!', category = 'success')
            app.logger.debug('Updating...')
            
            
            if mail:
                msg = Message("Hello",
                              sender="ilya.bagrak@gmail.com",
                              recipients=["ilya.bagrak+me@gmail.com"])
                msg.body = "Hello, world!"
                mail.send(msg)
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
            
            # session expired (?)
            if not 'pitches' in session:
                session['pitches'] = [{'name' : project.title, 'url' : project.unique_url}]
                session.permanent = True
                
            # update cookie if name changed
            for pitch in session['pitches']:
                if pitch['url'] == unique_url:
                    pitch['name'] = project.title
            
            session.modified = True
                    
            flash('Updated!', category = 'success')
            app.logger.debug('Updating...')
            return redirect(url_for('show_project', unique_url=unique_url))
        else: 
            flash(get_errors(form), category = 'error')
            
    form = ProjectForm(obj=project)
    return render_template('new_project.html', form=form, update = True)

if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
    