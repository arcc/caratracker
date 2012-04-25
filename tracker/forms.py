from os import path

from flask.ext.uploads import (UploadSet, configure_uploads, AllExcept, SCRIPTS,
                               EXECUTABLES)
from flask.ext.wtf import (Form, TextField, TextAreaField, BooleanField,
                           SelectField, RadioField, PasswordField, FileField,
                           QuerySelectField,DateField,
                           Required, Length, Optional, Email, NumberRange,
                           EqualTo, SubmitField, file_allowed)

from . import models
from . import app

upload_dir = lambda app: path.join(app.instance_path,'upload')

allowed = UploadSet('allowed', AllExcept(SCRIPTS + EXECUTABLES), 
                    default_dest = upload_dir)
configure_uploads(app, (allowed))

def category_query():
    return models.Category.query

class Create(Form):
    title=TextField('Subject', validators=[Length(3),Required()])
    description=TextAreaField('Description', validators=[Length(3),Optional()])
    category=QuerySelectField('Category', get_label='name', 
            query_factory=category_query, validators=[Optional()])
    account=TextField('Account', validators=[Length(3),Optional()])
    file_upload=FileField('Attachment', validators=[file_allowed(allowed, 
                                        "Unsupported File Type")])

class Ticket(Create):
    due=DateField('Due Date', validators=[Optional()])
    status=TextField('Status')
    approved=BooleanField('Approved')
    approved_by=TextField('Approved By')
    cost=TextField('Cost')
    comment=TextAreaField('Comment', validators=[Length(3),Optional()])
    priority=SelectField('Priority', choices=[(0,'None'), (1,'Lowest'),
        (2,'Low'), (3,'Normal'), (4, 'High'), (5,'URGENT')], coerce=int,
        validators=[NumberRange(0,5)])

class Note(Form):
    text=TextAreaField('New Note')

class Message(Form):
    text=TextAreaField('New Message')

class Category(Form):
    name=TextField('New Category')
    description=TextAreaField('Description')
    frontpage=BooleanField('On Homepage')
    submit = SubmitField('Add Category')

class Login(Form):
    openid=TextField('OpenID')

class Profile(Form):
    name=TextField('Full Name', validators=[Required()])
    email=TextField('Email', validators=[Required(),Email()])
    student_id=TextField('Student ID', validators=[Required()])

