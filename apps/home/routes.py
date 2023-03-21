# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us

https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application#step-4-displaying-a-single-record

"""
from apps import db
from apps.config import ROOT_DIR
from apps.home import blueprint
from apps.authentication.models import (Todos, economic_balancesheet, 
checking_transactions, credit_card_transactions, Upcoming_transactions)
from apps.authentication.forms import CreateTodoForm
from flask import render_template, request
from flask_login import (
    current_user,
    login_required
)

from jinja2 import TemplateNotFound
from sqlalchemy import desc, asc
from sqlalchemy.sql import func

import os
import pandas as pd
import gspread
from datetime import datetime, timedelta


@blueprint.route('index')
@login_required
def index():

    return render_template('home/index.html', segment='index')

@blueprint.route('<template>/')
@login_required
def route_template(template):

    # Detect the current page
    segment = get_segment(request)

    if template == 'todo-form':

        create_todo_form = CreateTodoForm(request.form)
            
        return render_template("accounts/todo_form.html", segment='To Do List',
        form=create_todo_form)

#    if template == 'akoya':

#        '''https://sandbox-idp.ddp.akoya.com/auth?connector=mikomo&client_id= 
#vkrpi6vz2dwfdokiznc3npqhi
#&redirect_uri= 
#https://recipient.ddp.akoya.com/flow/callback
# &response_type=code&scope=openid email profile offline_access'''
            
#        return render_template("accounts/todo_form.html", segment='To Do List',
#        form=create_todo_form)

    if template == 'todolist':
        
        todo_list = Todos.query.all()

        return render_template("home/todolist.html", segment='To Do List',
        db_todos = todo_list)

    if template == 'profile':

        print(current_user)

        return render_template("home/profile.html", segment='To Do List')
        
    if template == 'projected-cash':

        #To be deprecated when i move the gsheets api call to a separate function
        # print(os.environ['tempGoogleCredentials'])

        # gc = gspread.service_account_from_dict(os.environ['tempGoogleCredentials'])
    
        # sh = gc.open("House Budget")

        # worksheet = sh.worksheet("upcoming_transactions")
        # dataframe = pd.DataFrame(worksheet.get_all_records())
        dataframe = pd.read_csv(os.path.join(ROOT_DIR, 'apps/static/data', 'upcoming.csv'))

        dataframe['date'] = pd.to_datetime(dataframe.date)
        dataframe = dataframe.sort_values(by='date')

        dataframe.to_sql('upcoming_transactions', con=db.engine, if_exists='replace')

        # worksheet = sh.worksheet("checking_transactions")
        # dataframe = pd.DataFrame(worksheet.get_all_records())
        dataframe = pd.read_csv(os.path.join(ROOT_DIR, 'apps/static/data', 'checking.csv'))

        dataframe['date'] = pd.to_datetime(dataframe.date)
        dataframe = dataframe.sort_values(by='date')

        dataframe.to_sql('checking_transactions', con=db.engine, if_exists='replace')
        # #deprecate up to here 

        upcoming_transactions = Upcoming_transactions.query.all()

        #df = pd.read_csv(os.path.join(ROOT_DIR, 'apps/static/data', 'upcoming.csv'))
        #df['date'] = pd.to_datetime(df.date)
        #df = df.sort_values(by='date')
        df = pd.read_sql('SELECT * FROM upcoming_transactions', db.engine, index_col = 'index')

        bills = df.loc[df['amount']<=0]
        bill_sum = bills['amount'].sum()
        bill_date = bills['date'].max()
        paychecks = df.loc[df['amount']>0]
        paycheck_sum = paychecks['amount'].sum()
        paycheck_date = paychecks['date'].max()
        min_date = df['date'].min()
        max_date = df['date'].max()

        df_checking = pd.read_sql('SELECT * FROM checking_transactions', db.engine, index_col = 'index')
        #df_checking = pd.read_csv(os.path.join(ROOT_DIR, 'apps/static/data', 'checking.csv'))
        df_checking['date'] = pd.to_datetime(df_checking.date).astype(str)
        df_checking['formatted_date'] = df_checking['date'].astype(str)

        new_row = pd.DataFrame({'description':'Checking balance', 'date':df_checking.date.iloc[-1], 
			'amount':df_checking.transaction_amount.sum()},index =[0])
        df = pd.concat([new_row, df]).reset_index(drop = True)
        df['date'] = pd.to_datetime(df.date)
        df = df.groupby(['date']).sum(numeric_only=True).reset_index()
        df['balance'] = df.amount.cumsum()
        df['balance_shift'] = df['balance'].shift(1,fill_value = 0)

        #To be deprecated when i move the gsheets api call to a separate function
        #os.remove(os.path.join(ROOT_DIR, 'apps\\static', 'authorized_user.json'))
        
        return render_template("home/projected-cash.html", segment='Projected cash transactions',
        upcoming_transactions = upcoming_transactions,
        bills = bill_sum, bill_date=bill_date,
        paychecks = paycheck_sum, paycheck_date=paycheck_date,
        min_date=min_date, max_date=max_date,
        dataframe = df.to_records())

    if template == 'spending-summary':
        
        credit = credit_card_transactions.query.order_by(asc(credit_card_transactions.date)).all()
        credit_update = db.session.query(credit_card_transactions.date).order_by(desc(credit_card_transactions.date)).first()
        credit_balance_list = db.session.query(credit_card_transactions.balance_amount).order_by(desc(credit_card_transactions.date)).all()
        credit_balance_current = credit_balance_list[0][0]
        credit_balance_chg = (credit_balance_list[0][0]-credit_balance_list[190][0])/credit_balance_list[190][0]
        credit_balance_avg = db.session.query(func.avg(credit_card_transactions.balance_amount).label('average')).all()
        
        checking = checking_transactions.query.order_by(asc(checking_transactions.date)).all()
        check_update = db.session.query(checking_transactions.date).order_by(desc(checking_transactions.date)).first()
        check_balance_list = db.session.query(checking_transactions.balance_amount).order_by(desc(checking_transactions.date)).all()
        check_balance_current = pd.DataFrame(db.session.query(checking_transactions.transaction_amount)).sum()[0]
        check_balance_chg = (check_balance_list[0][0]-check_balance_list[190][0])/check_balance_list[190][0]
        check_balance_avg = db.session.query(func.avg(checking_transactions.balance_amount).label('average')).all()

        df_category = pd.DataFrame(db.session.query(credit_card_transactions.date))
        df_category['amount'] = pd.DataFrame(db.session.query(credit_card_transactions.amount))
        df_category['category'] = pd.DataFrame(db.session.query(credit_card_transactions.category))
        df_category = df_category.groupby(['category']).sum(numeric_only=True).reset_index()
        df_category = df_category[~df_category['category'].isin(['BALANCE','Payment/Credit'])]
        df_category['amount'].astype(int)

        df_balancesheet = pd.DataFrame(db.session.query(economic_balancesheet.account))
        df_balancesheet['amount'] = pd.DataFrame(db.session.query(economic_balancesheet.balance_amount))
        savings_amount = df_balancesheet.loc[df_balancesheet['account']=='Citi savings']['amount'].to_list()[0]
        
        return render_template("home/spending-summary.html", segment='historical spending',
        credits = credit, 
        credit_update = credit_update,
        credit_balance_current = credit_balance_current,
        credit_balance_chg=credit_balance_chg, 
        checking = checking, 
        checking_update = check_update,
        check_balance_current = check_balance_current,
        check_balance_chg=check_balance_chg,
        df_category = df_category.to_records(),
        check_balance_avg = check_balance_avg,
        credit_balance_avg = credit_balance_avg,
        savings_amount = savings_amount)

    if template == 'monthly-budget':

        # get today's datetime
        input_dt = datetime.today()
        # get first date of current month
        first_day_month = input_dt.replace(day=1)

        next_month = input_dt.replace(day=28) + timedelta(days=4)
        last_day_month = next_month - timedelta(days=next_month.day)
                
        df_credit_cards = pd.DataFrame(db.session.query(credit_card_transactions.date))
        df_credit_cards['date'] = pd.to_datetime(df_credit_cards.date)
        df_credit_cards['amount'] = pd.DataFrame(db.session.query(credit_card_transactions.amount))
        df_credit_cards['transaction_amount'] = pd.DataFrame(db.session.query(credit_card_transactions.transaction_amount))
        df_credit_cards['category'] = pd.DataFrame(db.session.query(credit_card_transactions.category))
        df_credit_cards['description'] = pd.DataFrame(db.session.query(credit_card_transactions.description))
        df_credit_cards['account'] = pd.DataFrame(db.session.query(credit_card_transactions.account))
        df_credit_cards['formatted_date'] = df_credit_cards['date'].astype(str)

        df_current_month = df_credit_cards[df_credit_cards['date'].dt.date >= first_day_month.date()]
        #df_current_month = df_current_month.loc[df_current_month['transaction_amount'].cumsum(),'balance_amount']
        df_current_month['balance_amount'] = df_current_month['transaction_amount'].cumsum().to_list()
        
        df_category = df_current_month
        
        df_category = df_category.groupby(['category']).sum(numeric_only=True).reset_index()
        df_category = df_category[~df_category['category'].isin(['BALANCE','Payment/Credit'])]
        df_category['amount_usd'] = df_category['amount'].astype(str)
        #df_category['amount_usd'] = df_category['amount'].apply(lambda x: format_currency(x, currency="USD", locale="en_US"))
        #print(df_category['amount_usd'].head())


        df_balancesheet = pd.DataFrame(db.session.query(economic_balancesheet.account))
        df_balancesheet['amount'] = pd.DataFrame(db.session.query(economic_balancesheet.balance_amount))
        savings_amount = df_balancesheet.loc[df_balancesheet['account']=='Citi savings']['amount'].to_list()[0]

        upcoming_transactions = Upcoming_transactions.query.all()

        df = pd.DataFrame(db.session.query(Upcoming_transactions.date))
        df['date'] = pd.to_datetime(df.date)
        df['amount'] = pd.DataFrame(db.session.query(Upcoming_transactions.amount))
        df['description'] = pd.DataFrame(db.session.query(Upcoming_transactions.description))
        df['payment_source'] = pd.DataFrame(db.session.query(Upcoming_transactions.payment_source))
        df = df[df['date'].dt.date  <= last_day_month.date()]
        
        bills = df.loc[df['amount']<=0]
        bill_sum = bills['amount'].sum()
        bill_date = bills['date'].max()
        paychecks = df.loc[df['amount']>0]['amount'].sum()
        
        current_spend = df_current_month.iloc[-1].balance_amount
        
        return render_template("home/monthly-budget.html", segment='monthly budget',
        df_category = df_category.to_records(),
        savings_amount = savings_amount,
        upcoming_transactions = upcoming_transactions,
        bills = bill_sum, 
        bill_date=bill_date,
        paychecks = paychecks, 
        df_credit_cards = df_current_month.to_records(),
        current_spend = current_spend)

    #try:

    if not template.endswith('.html'):
        template += '.html'

    # Serve the file (if exists) from app/templates/home/FILE.html
    return render_template("home/" + template, segment=segment)
    #return render_template(template, segment=segment)

    #except TemplateNotFound:
    #    return render_template('home/page-404.html'), 404

    #except:
    #    return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


