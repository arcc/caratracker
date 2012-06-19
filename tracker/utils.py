from hashlib import md5
from os import path, unlink

from werkzeug import secure_filename
from flask import (make_response,redirect, url_for,
                    render_template,json,request,flash,session)

from itsdangerous import URLSafeSerializer, BadSignature

from . import app
from . import models
from . import forms

serializer = URLSafeSerializer(app.config['SIGNING_KEY'])

def NYI(layout='layout.html'):
    return render_template('message.html', heading="Not Yet Implemented",
        message="Sorry for the inconvenience, this page is not yet complete",
        layout=layout)

def delete_ticket_cascade(ticket):
    for message in ticket.messages:
        models.db.session.delete(message)
    for note in ticket.notes:
        models.db.session.delete(note)
    for f in ticket.files:
        unlink(path.join(forms.upload_dir(app),f.filename))
        models.db.session.delete(f)
    models.db.session.commit()
    models.db.session.delete(ticket)
    models.db.session.commit()

def new_file(attachment, id):
    f = models.File()
    f.name = secure_filename(attachment.filename)
    #f.filename = md5(attachment.stream.getvalue()).hexdigest()
    f.filename = md5(str(attachment.filename)+str(id)).hexdigest()
    forms.allowed.save(attachment,name=f.filename)
    f.ticket_id = id
    models.db.session.add(f)
    models.db.session.commit()


