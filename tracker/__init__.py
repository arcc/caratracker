from hashlib import md5
from functools import wraps

from werkzeug import secure_filename
from flask import (Flask, make_response,redirect, url_for,
                    render_template,json,request,flash,session,
                    send_from_directory,abort,)
from flask.ext.openid import OpenID

app = Flask(__name__, static_url_path='/static', instance_relative_config=True)
app.config.from_object('%s.config'%__name__)
app.config.from_pyfile('config.py', silent=True)


from . import models
from . import forms
from . import jinjaconfig
from . import admin
from . import utils
from . import tasks
from .log import *

from .auth import *

@app.route('/')
def index():
    categories = models.Category.query
    categories = categories.filter(models.Category.frontpage==True).all()
    print [ x.id for x in categories ]
    return render_template('index.html', categories=categories)

@app.route('/create', methods=['POST','GET'])
@login_required
def create():
    cat = models.Category.query.get(request.args.get('cat',1))
    form = forms.Create()
    form.category.data=cat
    if form.validate_on_submit():
        ticket = models.Ticket()
        form.populate_obj(ticket)
        ticket.user_id = g.user.id
        models.db.session.add(ticket)
        models.db.session.commit()
        attachment = form.file_upload.data
        if attachment:
            utils.new_file(attachment, ticket.id)
        tasks.send_confirmation(ticket.id)
        tasks.send_alert(ticket.id)
        return redirect(url_for('confirmation'))
    
    return render_template("create.html",form=form, catid=cat.id)

@app.route('/confirmation',methods=['GET'])
@login_required
def confirmation():
    return render_template("confirmation.html")

def referrer_verified(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        referrer = request.view_args.get('referrer',None)
        if referrer is None:
            abort(404)
        bad_referrer = render_template('message.html',layout="layout.html",
            heading="Invalid Request Referrer", 
            message="""Please check the link that you recieved. If you think you
            are recieving this error in error, please contact the CARA
            Office.""")
        try:
            id = utils.serializer.loads(referrer)
        except utils.BadSignature:
            return bad_referrer

        ticket = models.Ticket.query.get(id)

        if g.user.id != ticket.user_id:
            session['denied']= "You are not the owner of this request"
            return redirect(url_for('permission_denied'))

        if ticket is None:
            return bad_referrer

        return f(*args, ticket=ticket, **kwargs)
    return decorated_function

@app.route('/review/<referrer>', methods=['GET','POST'])
@login_required
@referrer_verified
def review(referrer, ticket):

    msgform = forms.Message()
    fileform = forms.Upload()

    return render_template('ticket.html',ticket=ticket, referrer=referrer,
            msgform=msgform, fileform=fileform)

@app.route('/review/message/<referrer>', methods=['POST'])
@login_required
@referrer_verified
def message(referrer, ticket):

    form = forms.Message()

    if form.validate_on_submit():
        message = models.Message()
        form.populate_obj(message)
        message.ticket_id = id
        message.user_id = g.user.id
        models.db.session.add(message)
        models.db.session.commit()
        tasks.send_reply(message.id)

    return redirect(url_for('review',referrer=referrer))

@app.route('/review/upload/<referrer>', methods=['POST'])
@login_required
@referrer_verified
def upload(referrer, ticket):
    form = forms.Upload()

    if form.validate_on_submit():
        attachment = form.file_upload.data
        if attachment:
            utils.new_file(attachment, ticket.id)

    return redirect(url_for('review',referrer=referrer))

@app.route('/user', methods=['GET','POST'])
@login_required
def user():
    user = g.user
    form = forms.Profile(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        models.db.session.commit()
        flash("Successfully Updated")
        return redirect(url_for('user'))
    return render_template('user.html',user=user,form=form)

@app.route('/uploaded/<int:id>', methods=['GET','POST'])
@login_required
def uploaded(id):
    f = models.File.query.get_or_404(id)
    return send_from_directory(forms.upload_dir(app), f.filename,
                               as_attachment=True, attachment_filename=f.name)
    
app.register_blueprint(admin.admin, url_prefix='/admin')
