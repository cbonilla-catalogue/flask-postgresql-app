# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, flash
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm, UpdateTodoForm, CreateTodoForm
from apps.authentication.models import Users, Todos

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg=f'Username {user} already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg=f'{email} already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)
                               

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.route('/todo_form/insert', methods=['POST'])
@login_required
def insert():
    todo = Todos(**request.form)
    db.session.add(todo)
    db.session.commit()
    return redirect('/todolist')

@blueprint.route('todo-update/<string:id_data>', methods = ['GET'])
@login_required
def read(id_data):
        
    todo_id = db.session.query(Todos.id).filter_by(id=id_data).first()
    todo_title = db.session.query(Todos.title).filter_by(id=id_data).first()
    todo_desc = db.session.query(Todos.desc).filter_by(id=id_data).first()

    return render_template("accounts/todo_update.html", segment='To Do List',
    title = todo_title, id=todo_id, desc=todo_desc)

@blueprint.route('/todo_form/delete/<string:id_data>', methods = ['GET'])
@login_required
def delete(id_data):

    Todos.query.filter_by(id=id_data).delete()
    db.session.commit()

    return redirect('/todolist')

@blueprint.route('/todo-update',methods=['POST'])
def todo_update():

    task = Todos.query.get_or_404(request.form['id'])

    task.title = request.form['title']
    task.desc = request.form['desc']
    db.session.commit()

    return redirect('/todolist')

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.errorhandler(403)
def access_forbidden(error):
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
