from flask import current_app
from threading import Thread
from app import db
from app.models import User, Account, Transaction, Voucher, Volunteer, PaymentCollection
from app.api_1_0.validation import isStrEmpty

def share_donation_time(user, amount):
    true_future_rate = 0.4
    real_mine_rate = 0.2
    loading_user_rate = 0.2
    first_referee_rate = 0.08
    second_referee_rate = 0.056
    third_referee_rate = 0.04
    fouth_referee_rate = 0.024

    # update user balance
    reason = '{0} loaded donation time'.format(user.volunteer_ref_id)

    # update True future account
    true_future_user = User.query.filter_by(phone_number='256780682677').first()
    update_balance(true_future_user, amount, true_future_rate, reason)

    # update Real Mine love account
    real_mine_user = User.query.filter_by(phone_number='256794019994').first()
    update_balance(real_mine_user, amount, real_mine_rate, reason)

    #update user balance
    update_balance(user, amount,loading_user_rate,reason)

    # get the first user
    first_referee = get_referee_user(user)
    if first_referee is None:
        rate = first_referee_rate + second_referee_rate + third_referee_rate + fouth_referee_rate
        update_balance(true_future_user, amount, rate, reason)
        return
    update_balance(first_referee, amount,first_referee_rate, reason)

    second_referee = get_referee_user(first_referee)
    if second_referee is None:
        rate = second_referee_rate + third_referee_rate + fouth_referee_rate
        update_balance(true_future_user, amount, rate, reason)
        return
    update_balance(second_referee, amount, second_referee_rate, reason)

    third_referee = get_referee_user(second_referee)
    if third_referee is None:
        rate = third_referee_rate + fouth_referee_rate
        update_balance(true_future_user, amount, rate, reason)
        return
    update_balance(third_referee, amount, third_referee_rate, reason)

    fourth_referee = get_referee_user(third_referee)
    if fourth_referee is None:
        update_balance(true_future_user, amount, fouth_referee_rate, reason)
        return
    update_balance(fourth_referee, amount,fouth_referee_rate, reason)


def update_account_async(app, user):
    with app.app_context():
        db.session.add(user)
        db.session.commit()


def update_account(user, **kwargs):
    app = current_app._get_current_object()
    thr = Thread(target=update_account_async, args=[app, user])
    thr.start()
    return thr


def update_balance(user, amount, rate, reason):
    # Update the user balance
    value = amount * rate * 0.5
    old_bal = user.account.account_balance
    old_vsse = user.account.vsse_balance
    user.account.account_balance = old_bal + value
    user.account.vsse_balance = old_vsse + value
    db.session.add(user)

    # Update the transaction logs
    reason = 'Donation Time from user {0}'.format(user.volunteer_ref_id)
    amt = amount * rate
    save_transaction(amt,user.account,'LoadedDonationTime',reason)

def save_transaction(amount,account,type,reason):
    transaction = Transaction(amount=amount, transaction_type=type,
                              transaction_status='Completed', reason=reason, account=account)
    db.session.add(transaction)
    db.session.commit()
    return transaction


def get_referee_user(user):
    vol = Volunteer.query.filter_by(tf_id=user.volunteer_ref_id).first()
    if vol.refered_id is None:
        return None
    elif isStrEmpty(vol.refered_id):
        return None
    user = User.query.filter_by(volunteer_ref_id=vol.refered_id).first()
    return user


def create_payment_collection(user, package, voucher):
    col = PaymentCollection(payer=user, package=package, voucher=voucher,
                            amount=package.amount, voucher_code=voucher.code)
    db.session.add(col)
    db.session.commit()
