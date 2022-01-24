from ..import db
from ..models import Transaction, User, Account
from flask import g, request, jsonify
from .decorators import check_token
from . import api
from .validation import isStrEmpty, isEmpty
from ..models import Voucher, Setting, User
import time
from app.modules.transactions import share_donation_time, create_payment_collection, save_transaction

@api.route('/load-donation',methods=['POST'])
@check_token()
def load_donation_time():
    user = g.current_user
    errors = {}
    if request.method == 'POST':
        result = request.get_json()
        code = result['code']
        if code is None or isStrEmpty(code):
            errors['code'] = 'This field is required'
    if not isEmpty(errors):
        res = jsonify({
            'errors': errors
        })
        res.status_code = 400
        return res
    voucher = db.session.query(Voucher).filter(Voucher.code==code).first()
    if voucher is None:
        errors['form'] = 'Invalid donation time code'
        return jsonify({
            'errors': errors
        }),400

    if not voucher.is_active:
        errors['form'] = 'Donation time voucher has already been used'
        return jsonify({
            'errors': errors
        }),400

    create_payment_collection(user,voucher.package,voucher)
    share_donation_time(user,voucher.package.amount)

    voucher.is_active = False
    db.session.add(voucher)
    db.session.commit()
    return jsonify({'status': 'Voucher code loaded successfully!'})

@api.route('/transactions',methods=['GET'])
@check_token()
def transactions():
    user = g.current_user
    transactions = Transaction.query.filter(Transaction.account_id==user.account.id).all()
    return jsonify({
        'transactions': [transaction.to_json() for transaction in transactions]
    }),200

@api.route('/get-rate',methods=['GET'])
@check_token()
def get_rate():
    setting = Setting.get_setting_by_name('GoalRate')
    return jsonify({
      'rate': setting.to_json()
    })

@api.route('/get-balance',methods=['GET'])
@check_token()
def get_balance():
    user = g.current_user
    return jsonify({'balance':{
                        'goalBalance': user.account.goals_balance,
                        'accountBalance': user.account.account_balance
                        }
                })

@api.route('/buy-goals',methods=['POST'])
@check_token()
def buy_goals():
    user = g.current_user
    errors = {}
    result = request.get_json()
    amount = result['ugxAmount']
    if amount is None:
        errors['ugxAmount'] = 'This field is required'
    if user.account.account_balance < amount:
        errors["ugxAmount"] = 'This amount cannot be greater than account balance'
    if not isEmpty(errors):
        res = jsonify({
            'errors': errors
        })
        res.status_code = 400
        return res
    setting = Setting.get_setting_by_name('GoalRate')
    goals = amount / int(setting.value)
    toOpeningBalance = user.account.goals_balance
    toClosingBalance =  toOpeningBalance + goals

    openingBalance = user.account.account_balance
    closingBalance = openingBalance - amount
    user.account.account_balance = closingBalance

    user.account.goals_balance = toClosingBalance
    db.session.add(user)
    transaction = save_transaction(amount,user.account,'BuyGoals','Bought goals')
    return jsonify({'balance': user.account.account_balance})

@api.route('/transfer-goals',methods=['POST'])
@check_token()
def transfer_goals():
    user = g.current_user
    errors = {}
    result = request.get_json()
    phoneNumber = result['accountNumber']
    amount = result['amount']
    if phoneNumber is None or isStrEmpty(phoneNumber):
            errors['accountNumber'] = 'This field is required'
    if amount is None:
            errors['amount'] = 'This field is required'
    if not isEmpty(errors):
        res = jsonify({
            'errors': errors
        })
        res.status_code = 400
        return res
    toAccUser = User.query.filter_by(phone_number=phoneNumber).first();
    if toAccUser is None:
        errors['accountNumber'] = 'User account with phone number does not exist'
        res = jsonify({
            'errors': errors
        })
        res.status_code = 400
        return res
    if user.account.goals_balance < amount:
        errors['amount'] = 'You do not have enough goals to share. Buy some goals'
        res = jsonify({
            'errors': errors
        })
        res.status_code = 400
        return res

    fromOpeningBalance = user.account.goals_balance
    fromClosingBalance = fromOpeningBalance - amount

    toOpeningBalance = toAccUser.account.goals_balance
    toClosingBalance =  toOpeningBalance + amount

    toAccUser.account.goals_balance = toClosingBalance
    user.account.goals_balance = fromClosingBalance
    db.session.add(toAccUser)
    db.session.add(user)
    transaction = save_transaction(amount,user.account,'ShareGoals','shared goals to {0}'.format(toAccUser.volunteer_ref_id))
    save_transaction(amount,toAccUser.account,'ShareGoals','Received goals from {0}'.format(user.volunteer_ref_id))
    return jsonify({'transaction': transaction.to_json()})

def verify_is_number(number):
    if not number.isdigit():
        return False
    return True

@api.route('/check-account/<acc>',methods=['GET'])
@check_token()
def check_account(acc):
    if acc is None or isStrEmpty(acc) or acc == '256':
        return jsonify({'error': 'This field is required'}),400
    if not verify_is_number(acc):
        return jsonify({'error': 'Phone number is invalid'}),400
    user = User.query.filter_by(phone_number=acc).first()
    if user is None:
        return jsonify({'error': 'Account with phone number does not exist'}),400
    return jsonify({'status': 'ok'}), 200