from datetime import date

from flask import (Blueprint, render_template, abort, request, url_for,
                    flash, redirect, make_response, g)

from . import app
from . import models
from . import forms
from . import utils
from .auth import admin_required

admin = Blueprint('admin', __name__, template_folder='templates',
                static_folder='static')

from .manage import *

@admin.route('/')
@admin_required
def index():
    tickets = models.Ticket.query.filter(models.Ticket.completed == False)
    tickets = tickets.order_by(models.Ticket.priority.desc()).all()
    return render_template('admin/index.html', tickets = tickets)

@admin.route('/ticket/<int:id>', methods=['POST','GET'])
@admin_required
def ticket(id):
    today = date.today()
    ticket = models.Ticket.query.get_or_404(id)
    form = forms.Ticket(obj=ticket)
    msg_form = forms.Message()
    note_form = forms.Note()
    if form.validate_on_submit():
        form.populate_obj(ticket)
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
        flash('Request #%s updated'%ticket.id)
    
    return render_template('admin/ticket.html', id = id, ticket=ticket,
            form=form,msg_form=msg_form, note_form=note_form, today=today)

@admin.route('/note/<int:id>', methods=['POST'])
@admin_required
def note(id):
    form = forms.Note()
    if form.validate_on_submit():
        note = models.Note()
        form.populate_obj(note)
        note.ticket_id = id
        models.db.session.add(note)
        models.db.session.commit()
    return redirect(url_for('.ticket',id=id))

@admin.route('/message/<int:id>', methods=['POST'])
@admin_required
def message(id):
    form = forms.Message()
    if form.validate_on_submit():
        message = models.Message()
        form.populate_obj(message)
        message.ticket_id = id
        models.db.session.add(message)
        models.db.session.commit()
    return redirect(url_for('.ticket',id=id))
    
@admin.route('/complete/<int:id>', methods=['POST'])
@admin_required
def complete(id):
    ticket = models.Ticket.query.get(id)
    if ticket is None:
        abort(404)
    ticket.completed = True
    models.db.session.add(ticket)
    models.db.session.commit()
    return redirect(url_for('.index'))

@admin.route('/create', methods=['POST','GET'])
@admin_required
def create():
    today = date.today()
    form = forms.Ticket()
    if form.validate_on_submit():
        ticket = models.Ticket()
        form.populate_obj(ticket)
        ticket.user_id = g.user.id
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
        flash('Request #%s created'%ticket.id)
        return redirect(url_for('.ticket',id=ticket.id))

    return render_template("admin/create.html",form=form, today=today)

@admin.route('/category/<int:id>', methods=['POST','GET'])
@admin_required
def category(id):
    tickets = models.Ticket.query.filter(models.Ticket.completed == False)
    tickets = tickets.filter_by(category_id=id)
    tickets = tickets.order_by(models.Ticket.priority.desc()).all()
    return render_template('admin/index.html', tickets = tickets)

@admin.route('/categories')
@admin_required
def categories():
    categories = models.Category.query.order_by('name').all()
    return render_template('admin/categories.html', categories = categories)

@admin.route('/users')
@admin_required
def users():
    users = models.User.query.order_by('name').all()
    return render_template('admin/users.html', users = users)

@admin.route('/user/<int:id>')
@admin_required
def user(id):
    user = models.User.query.get_or_404(id)
    return render_template('admin/user.html', user = user)

@admin.route('/archives')
@admin_required
def archives():
    tickets = models.Ticket.query.filter(models.Ticket.completed == True)
    tickets = tickets.order_by(models.Ticket.priority.desc()).all()
    return render_template('admin/index.html', tickets = tickets)

@admin.route('/archives/categories')
@admin_required
def archives_categories():
    categories = models.Category.query.order_by('name').all()
    return render_template('admin/archive_categories.html', 
            categories = categories)

