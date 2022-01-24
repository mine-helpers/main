from ..models import User, Transaction, Account
from . import api
from flask import jsonify, request, g
from .decorators import check_token
from ..import db
import requests
from .validation import isStrEmpty
from datetime import datetime


@api.route('/goals',methods=['POST','GET'])
@check_token()
def purchase_goals():
    user = g.current_user
    try:
        if request.method == 'POST':
            #TODO: get the goal rate from the database
            goal_rate = 10000
            data = request.get_json()
            ugxAmount  = data['amount']
            if isStrEmpty(ugxAmount):
                return jsonify({
                    'errors':{
                        'amount': 'This field is required'
                    }
                }),400
            goals = int(ugxAmount) / goal_rate
            account = user.account
            account.account_balance = account.account_balance + goals
            db.session.add(account)
            db.session.commit()
            return jsonify(account.to_json()),200
        else:
            account = user.account
            return jsonify(account.to_json()),200
    except Exception as e:
        return jsonify({
            'errors':{
                'form': e.__str__()
            }
        }), 500

@api.route('/goal-rate',methods=['GET'])
@check_token()
def get_goal_rate():
    try:
        return jsonify({
            'goalRate': 1000
        })
    except Exception as e:
        return jsonify({
            'errors':{
                'form': e.__str__()
            }
        }), 500

@api.route('/recon',methods=['GET'])
def reconcile_balances():
    # trans = Transaction.query.filter(Transaction.timestamp>=datetime(2017,10,17)).filter(Transaction.timestamp<=datetime(2017,10,18)).filter(Transaction.transaction_type=='LoadedDonationTime').all()
    # for tran in trans:
    #     acc = tran.account
    #     acc.vsse_balance -= tran.amount * 0.5
    #     acc.account_balance -= tran.amount * 0.5
    #     db.session.add(acc)
    #     db.session.delete(tran)
    #     db.session.commit()
    accs  = Account.query.all()
    for acc in accs:
        if acc.account_balance < 0:
            acc.account_balance = account_balance * -1
        if acc.vsse_balance < 0:
            acc.vsse_balance = vsse_balance * -1
        db.session.add(acc)
        db.session.commit()

    return jsonify({
             'transactions': 'success'
              })