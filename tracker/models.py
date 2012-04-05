from datetime import date

from flask.ext.sqlalchemy import SQLAlchemy

from . import app

db = SQLAlchemy(app)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(150))
    description=db.Column(db.Text())
    created=db.Column(db.Date)
    due=db.Column(db.Date)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id=db.Column(db.Integer, db.ForeignKey('category.id'))
    description=db.Column(db.Text())
    files = db.relationship("File",backref="ticket",lazy='dynamic')
    account=db.Column(db.String(50))
    approved=db.Column(db.Boolean, default=False)
    approved_by=db.Column(db.String(150))
    notes = db.relationship("Note",backref="ticket",lazy='dynamic')
    messages = db.relationship("Message",backref="ticket",lazy='dynamic')
    comment = db.Column(db.Text())
    status=db.Column(db.String(50))
    recall = db.Column(db.String(150))
    priority = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)

    def __init__(self):
        self.created = date.today()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    description=db.Column(db.Text())
    frontpage=db.Column(db.Boolean, default=False)
    tickets = db.relationship("Ticket",backref="category",lazy='dynamic')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    email=db.Column(db.String(150))
    student_id=db.Column(db.String(10))
    openid=db.Column(db.String(100))
    approved=db.Column(db.Boolean,default=False)
    admin=db.Column(db.Boolean, default=False)
    can_elevate=db.Column(db.Boolean, default=False)
    suspended=db.Column(db.Boolean, default=False)
    tickets = db.relationship("Ticket",backref="user",lazy='dynamic')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text=db.Column(db.Text())
    created=db.Column(db.Date)
    ticket_id=db.Column(db.Integer, db.ForeignKey('ticket.id'))

    def __init__(self):
        self.created = date.today()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text=db.Column(db.Text())
    created=db.Column(db.Date)
    ticket_id=db.Column(db.Integer, db.ForeignKey('ticket.id'))

    def __init__(self):
        self.created = date.today()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    filename=db.Column(db.String(300))
    created=db.Column(db.Date)
    ticket_id=db.Column(db.Integer, db.ForeignKey('ticket.id'))

    def __init__(self):
        self.created = date.today()
