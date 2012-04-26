from flask import (render_template, abort, request, url_for,
                    flash, redirect, make_response)

from .admin import admin
from . import models
from . import forms
from . import utils
from .auth import login_required,admin_required,elevation_required

@admin.route('/manage/categories', methods=['GET','POST'])
@login_required
@admin_required
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
@admin_required
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
@admin_required
def manage_users():
    users = models.User.query.filter_by(approved=False).all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/manage/users/suspended')
@admin_required
def manage_suspended_users():
    users = models.User.query.filter_by(suspended=True).all()
    return render_template('admin/manage_suspended_users.html', users=users)

@admin.route('/manage/users/approve/<int:id>')
@admin_required
def approve_user(id):
    user = models.User.query.get_or_404(id)
    user.approved=True
    models.db.session.commit()
    flash('User %s approved.'%user.name)
    tasks.send_approved(id)

    return redirect(url_for('.manage_users'))

@admin.route('/manage/users/deny/<int:id>')
@admin_required
def deny_user(id):
    user = models.User.query.get_or_404(id)
    for ticket in user.tickets:
        utils.delete_ticket_cascade(ticket)
    models.db.session.delete(user)
    models.db.session.commit()
    flash('User %s was denied.'%user.name)

    return redirect(url_for('.manage_users'))

@admin.route('/manage/users/suspend/<int:id>')
@admin_required
def suspend_user(id):
    user = models.User.query.get_or_404(id)
    user.suspended = True
    models.db.session.commit()
    flash('User %s was suspended.'%user.name)

    return redirect(url_for('.user', id=id))

@admin.route('/manage/users/activate/<int:id>')
@admin_required
def activate_user(id):
    user = models.User.query.get_or_404(id)
    user.suspended = False
    models.db.session.commit()
    flash('User %s was activated.'%user.name)

    return redirect(url_for('.user', id=id))

@admin.route('/manage/users/elevate/<int:id>')
@admin_required
def elevate_user(id):
    user = models.User.query.get_or_404(id)
    user.admin=True
    models.db.session.commit()
    flash('User %s elevated to admin.'%user.name)

    return redirect(url_for('.user', id=id))

@admin.route('/manage/users/lower/<int:id>')
@admin_required
def lower_user(id):
    user = models.User.query.get_or_404(id)
    user.admin=False
    user.can_elevate=False
    models.db.session.commit()
    flash('User %s has lost admin status.'%user.name)

    return redirect(url_for('.user', id=id))

@admin.route('/manage/users/bless/<int:id>')
@admin_required
@elevation_required
def bless_user(id):
    user = models.User.query.get_or_404(id)
    user.can_elevate=True
    models.db.session.commit()
    flash('User %s granted elevation privileges.'%user.name)

    return redirect(url_for('.user', id=id))

@admin.route('/manage/users/damn/<int:id>')
@admin_required
@elevation_required
def damn_user(id):
    user = models.User.query.get_or_404(id)
    user.can_elevate=False
    models.db.session.commit()
    flash('User %s has lost elevation privileges.'%user.name)

    return redirect(url_for('.user', id=id))
