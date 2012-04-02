from datetime import date

from flask import (Blueprint, render_template, abort, request, url_for,
                    flash, redirect, make_response)

from . import app
from . import models
from . import forms
from . import utils

admin = Blueprint('admin', __name__, template_folder='templates',
                static_folder='static')

@admin.route('/')
def index():
    tickets = models.Ticket.query.filter(models.Ticket.completed == False)
    tickets = tickets.order_by(models.Ticket.priority.desc()).all()
    return render_template('admin/index.html', tickets = tickets)

@admin.route('/ticket/<int:id>', methods=['POST','GET'])
def ticket(id):
    today = date.today()
    ticket = models.Ticket.query.get_or_404(id)
    form = forms.Ticket(obj=ticket)
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
            form=form, today=today)

@admin.route('/create', methods=['POST','GET'])
def create():
    today = date.today()
    form = forms.Ticket()
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
        flash('Request #%s created'%ticket.id)
        return redirect(url_for('.ticket',id=ticket.id))

    return render_template("admin/create.html",form=form, today=today)

@admin.route('/category/<int:id>', methods=['POST','GET'])
def category(id):
    tickets = models.Ticket.query.filter(models.Ticket.completed == False)
    tickets = tickets.filter_by(category_id=id)
    tickets = tickets.order_by(models.Ticket.priority.desc()).all()
    return render_template('admin/index.html', tickets = tickets)

@admin.route('/categories')
def categories():
    categories = models.Category.query.order_by('name').all()
    return render_template('admin/categories.html', categories = categories)

@admin.route('/users')
def users():
    users = models.User.query.order_by('name').all()
    return render_template('admin/users.html', users = users)

@admin.route('/user/<int:id>')
def user(id):
    user = models.User.query.get_or_404(id)
    return render_template('admin/user.html', user = user)

@admin.route('/manage/categories', methods=['GET','POST'])
def manage_categories():
    categories = models.Category.query.all()

    form = forms.Category()
   
    if form.validate_on_submit():
        category = models.Category()
        form.populate_obj(category)
        models.db.session.add(category)
        models.db.session.commit()
        return redirect(url_for('.manage_categories'))

    return render_template('admin/manage_cats.html', form=form,
            categories=categories)

@admin.route('/manage/category/<int:id>', methods=['GET','POST'])
def manage_category(id):
    category = models.Category.query.get_or_404(id)
    form = forms.Category(obj=category)

    if form.validate_on_submit():
        form.populate_obj(category)
        models.db.session.commit()
        flash("Category %s updated."%category.name)
        return redirect(url_for('.manage_categories'))

    return render_template('admin/edit_cat.html', form=form, id=id)

@admin.route('/manage/users')
def manage_users():
    users = models.User.query.filter_by(approved=False).all()
    return render_template('admin/manage_users.html')

@admin.route('/manage/users/approve/<int:id>')
def approve_user(id):
    user = models.User.query.get_or_404(id)
    user.approved=True
    models.db.session.commit()
    flash('User %s approved.'%user.name)

    return redirect(url_for('manage_users'))
