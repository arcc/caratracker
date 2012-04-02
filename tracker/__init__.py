from hashlib import md5

from werkzeug import secure_filename
from flask import (Flask, make_response,redirect, url_for,
                    render_template,json,request,flash,session)

app = Flask(__name__)
app.config.from_object('%s.config'%__name__)

from . import models
from . import forms
from . import jinjaconfig
from . import admin
from . import utils


@app.route('/')
def index():
    categories = models.Category.query
    categories = categories.filter(models.Category.frontpage==True).all()
    print [ x.id for x in categories ]
    return render_template('index.html', categories=categories)

@app.route('/create', methods=['POST','GET'])
def create():
    cat = models.Category.query.get(request.args.get('cat',1))
    form = forms.Create()
    form.category.data=cat
    if form.validate_on_submit():
        ticket = models.Ticket()
        form.populate_obj(ticket)
        ticket.created=date.today()
        models.db.session.add(ticket)
        models.db.session.commit()
        attachment = form.file_upload.data
        if attachment:
            f = models.File()
            f.name = secure_filename(attachment.filename)
            f.filename = md5(attachment.stream.getvalue()).hexdigest()
            forms.allowed.save(attachment,name=f.filename)
            f.ticket_id = ticket.id
            models.db.session.add(f)
            models.db.session.commit()
        return redirect(url_for('confirmation'))
    
    return render_template("create.html",form=form)

@app.route('/confirmation',methods=['GET'])
def confirmation():
    return render_template("confirmation.html")

app.register_blueprint(admin.admin, url_prefix='/admin')
