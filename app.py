import os
from datetime import timedelta

try:
    import simplejson as json
except ImportError:
    import json
    
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify, make_response
app = Flask(__name__)

from flask.ext.mongokit import MongoKit, Document
import datetime, string, random
from flaskext.wtf import Form, TextField, TextAreaField, SubmitInput, Label
from wtforms import ValidationError
from wtforms.validators import Email
from flaskext.mail import Mail, Message

app.debug= True
app.config['TESTING'] = True
app.config['SECRET_KEY'] = "5A9580DAAA1C8736783C3C0968B89FEC5337AC49286E6FA4D2AFD3400FB90235"
app.permanent_session_lifetime = timedelta(days = 365)

# mongo configuration
if os.environ.get('MONGOHQ_URL'):
    app.debug = False
    app.config.update(MONGODB_HOST = os.environ.get('MONGOHQ_URL'),
                      MONGODB_DATABASE = 'app4005374')

CSRF_ENABLED = True

# smtp configuration
if os.environ.get('SENDGRID_USERNAME'):
    app.config['TESTING'] = False
    
app.config.update(
                  #EMAIL SETTINGS
                  MAIL_SERVER = 'smtp.sendgrid.net',
                  MAIL_PORT = 587,
                  MAIL_USE_SSL = False,
                  MAIL_DEBUG = app.debug,
                  MAIL_USERNAME = os.environ.get('SENDGRID_USERNAME'),
                  MAIL_PASSWORD = os.environ.get('SENDGRID_PASSWORD'),
                  MAIL_FAIL_SILENTLY = False,
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
    default_values = {'created_at':datetime.datetime.utcnow, 'title':u'*', 'tagline':u''}
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

def email_or_empty():
    def _email_or_empty(form, field):
        if len(field.data) > 0:
            Email()(form, field)
    
    return _email_or_empty

def get_errors(form):
    err = ''
    for v in form.errors.values():
        err = v[0] + ' ' + err
    
    return err

class ProjectForm(Form):
    title = TextField("Title", [required(), length(max = 50, words = False)])
    tagline = TextField("Tagline", [required(), length(max = 10)])
    tweet = TextAreaField("One Tweetful", [length(max = 140, words = False)])    
    blurb = TextAreaField("Email Blurb + Elevator Pitch", [length(max = 100)])
    
    twitter_desc = TextAreaField("Twitter Description")
    facebook_desc = TextAreaField("Facebook Description")
    
    email_addr = TextField("", [email_or_empty()])

@app.route("/", methods=["GET", "POST"])
def home():
    if not 'pitches' in session:
        session['pitches'] = []
        session.permanent = True
            
    project = db.Project()
    project.unique_url = create_url()
    project.save()
    
    session['pitches'].append({'name' : project.title, 'url' : project.unique_url})
    session.modified = True
    
    return redirect(url_for('show_project', unique_url = project.unique_url))

@app.route('/favicon.ico')
def favicon():
    return abort(404) 
              

@app.route('/<unique_url>', methods=["GET", "POST"])
def show_project(unique_url):
    form = ProjectForm(request.form)
    project = db.Project.find_one({'unique_url' : unique_url})
    
    # POST
    if request.method == "POST" and "_email" in request.form.values():
        if not form.email_addr.data: 
            flash('Email missing', category='error')
                
        elif mail: 
            msg = Message(form.title.data + " on Mission Statement",
                          sender="ilya.bagrak@gmail.com",
                          recipients=[form.email_addr.data])
            msg.body = """Hello, %s! 
                    
                          Here is the permanent link to your \"%s\" pitch on Mission Statement (http://missionstatement.herokuapp.com). 
                          
                          %s
                          
                          Flex that idea muscle and keep them coming!
                          
                          Yours Truly, 
                          
                          Ilya and Tyler
                          
                          PS: Let us know how we can keep Mission Statement better, or better yet send us a pitch.
                        """ % (form.email_addr.data, form.title.data, "http://missionstatement.herokuapp.com/" + unique_url)
            mail.send(msg)
                
            app.logger.debug('Emailing...')
            flash('Link sent.', category='success')
        else:
            flash(get_errors(form), category='error')
                    
        return redirect(url_for('show_project', unique_url=unique_url))
    
    # GET
    form = ProjectForm(obj=project)
    app.logger.debug(project)
    return render_template('new_project.html', form=form, unique_url = project.unique_url, update = True)

@app.route('/api/v1/pitch/<unique_url>', methods=["POST"])
def update_project(unique_url):
    app.logger.debug(request.json)
    
    project = db.Project.find_one({'unique_url' : unique_url})
    if not project: 
        response = jsonify({'code': 404,'message': 'No pitch found.'})
        response.status_code = 404
        return response
    
    payload = json.loads(request.data)
    for k in payload.keys(): 
        if k in Project.structure: 
            project[k] = payload[k]
            if k == 'title': 
                for pitch in session['pitches']:
                    if pitch['url'] == unique_url:
                        pitch['name'] = project.title
                session.modified = True
        else: 
            response = jsonify({'code': 4,'message': 'Unknown field.'})
            response.status_code = 404
            return response
            
    project.save()
    return jsonify(code = 2, message = "Success")

if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
    
