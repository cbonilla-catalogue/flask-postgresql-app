# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us

https://stackoverflow.com/questions/59412834/how-to-filter-a-sql-query-on-columns-in-sqlalchemy

"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

class Todos(db.Model):

    __tablename__ = 'Todo_list'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    desc = db.Column(db.String())
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)
    
    def __repr__(self):
        return str(self.title)

class economic_balancesheet(db.Model):

    __tablename__ = 'economic_balancesheet'

    index = db.Column(db.Integer, primary_key=True)
    balance_amount = db.Column(db.Integer)
    account = db.Column(db.String())
    account_type = db.Column(db.String())
    maturity_date = db.Column(db.Date())
    valuation_date = db.Column(db.Date())
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)
    
    def __repr__(self):
        return str(self.balance_amount)

class checking_transactions(db.Model):

    __tablename__ = 'checking_transactions'

    index = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String())
    category = db.Column(db.String())
    type = db.Column(db.String())
    amount = db.Column(db.Integer)
    account = db.Column(db.String())
    account_type = db.Column(db.String())
    transaction_amount = db.Column(db.Integer)
    date = db.Column(db.String())
    balance_amount = db.Column(db.Integer)

    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)
    
    def __repr__(self):
        return str(self.transaction_amount)

class credit_card_transactions(db.Model):

    __tablename__ = 'credit_card_transactions'

    index = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String())
    category = db.Column(db.String())
    type = db.Column(db.String())
    amount = db.Column(db.Integer)
    account = db.Column(db.String())
    account_type = db.Column(db.String())
    transaction_amount = db.Column(db.Integer)
    date = db.Column(db.String())
    balance_amount = db.Column(db.Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)
    
    def __repr__(self):
        return str(self.transaction_amount)

class Upcoming_transactions(db.Model):

    __tablename__ = 'upcoming_transactions'

    index = db.Column(db.Integer, primary_key=True)
    description =db.Column(db.String())
    date = db.Column(db.String())
    amount = db.Column(db.Integer)
    payment_source = db.Column(db.String())

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)
    
    def __repr__(self):
        return str(self.amount)

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
