# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import hashlib
import binascii

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def hash_pass(password):
    """Hash a password for storing."""

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)  # return bytes


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""

    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

class AmortizationSchedule_Monthly:
    '''Desgined to work with a monthly payment schedule
    in the'''
    def __init__(self, principal: float, 
                 reported_interest_rate: float,
                  interest_daycount:str,
                  period:int):
        self.principal = principal
        self.reported_interest_rate = reported_interest_rate
        self.interest_daycount = interest_daycount
        self.period = period
        #self.calculated_interest_rate = self.calc_interest_rate()
        self.amortization_schedule = self.build_amortization_schedule()

    def calc_interest_rate(self,reported_interest_rate):
        interest_rate = reported_interest_rate/12
        return interest_rate
    
    def calc_scheduled_payment(self, principal,period):
        rate = self.calc_interest_rate(self.reported_interest_rate)
        #if period == 1:
        #    payment = principal*(1+rate)
        #else:
        payment = (principal * rate)/(1-(1+rate) ** -period)

        return payment
    
    def make_payment(self,principal, mpr, monthly_payment):
        '''Makes a 'payment' by subtracting and updated payment amount from the 
    principal. Returns the principal remaining, and the amount of principal and interest paid
    '''
        current_interest_payment = principal * mpr
        current_principal_payment = monthly_payment - current_interest_payment
    
        principal -= current_principal_payment
    
        return [round(principal, 2), round(current_principal_payment, 2), round(current_interest_payment, 2)] 

    
    def build_amortization_schedule(self):
        payments = [[self.principal, 0, 0, 0]]
        total_interest = 0

        principal = self.principal
        period = self.period
        
        mpr = self.calc_interest_rate(self.reported_interest_rate)
        reg_payment = self.calc_scheduled_payment(principal,period)
        #reg_payment = 1560.83
        
        while principal > 0 and period > 0:
            payment = self.make_payment(principal,mpr,reg_payment)
            principal = payment[0]

            period -= 1
            total_interest += payment[2]
            payment.append(total_interest)
            payments.append(payment)

        amortization_table = pd.DataFrame(data=payments,
                                      columns=['Principal Remaining',
                                              'Current Principal Payment',
                                              'Current Interest Payment',
                                              'Total Interest Paid'])
        
        amortization_table['Payment'] = reg_payment
    
        #amortization_table.loc[mask, 'c'] = 42

        amortization_table.loc[self.period,'Principal Remaining']=0
        amortization_table.loc[self.period,'Current Principal Payment']=amortization_table.loc[self.period-1,'Principal Remaining']
        amortization_table.loc[self.period,'Payment']=(amortization_table.iloc[-1]['Current Principal Payment']+amortization_table.iloc[-1]['Current Interest Payment'])

        return amortization_table