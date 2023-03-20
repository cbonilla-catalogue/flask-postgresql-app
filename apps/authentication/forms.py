# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    username = TextField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = TextField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = TextField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])

class CreateTodoForm(FlaskForm):
    title = TextField('Title',
                         id='title_create',
                         validators=[DataRequired()])
    desc = TextField('Description',
                      id='desc_create')

class UpdateTodoForm(FlaskForm):
    id = TextField('Id',
                         id='id_update',
                         validators=[DataRequired()])
    title = TextField('Title',
                         id='id_update',
                         validators=[DataRequired()])
    desc = TextField('Description',
                      id='id_update')
