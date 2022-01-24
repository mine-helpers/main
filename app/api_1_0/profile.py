from ..models import User, Transaction
from . import api
from flask import jsonify, request, g
from .decorators import check_token
from ..import db
from ..models import Volunteer
from .validation import isStrEmpty
import time

@api.route('/account',methods=['GET'])
@check_token()
def account():
    #get the current user and there account details
    user = g.current_user
    transactions = Transaction.query.filter(Transaction.account_id==user.account.id).order_by(Transaction.timestamp.desc()).all()
    return jsonify({
      'account': user.account.to_json(),
      'transactions': [transaction.to_json() for transaction in transactions]
    })

@api.route('/network',methods=['GET'])
@check_token()
def get_network():
    user = g.current_user
    net_one = Volunteer.query.filter_by(refered_id=user.volunteer_ref_id).all()
    count = len(net_one)
    for vol in net_one:
        net_two = Volunteer.query.filter_by(refered_id=vol.tf_id).all()
        count += len(net_two)
        for v in net_two:
            net_three = Volunteer.query.filter_by(refered_id=v.tf_id).all()
            count += len(net_three)
            for _v in net_three:
                net_four = Volunteer.query.filter_by(refered_id=_v.tf_id).all()
                count += len(net_four)
    return jsonify({'count': count,'volunteerId': user.volunteer_ref_id})

@api.route('/profile',methods=['GET'])
@check_token()
def profile():
    user = g.current_user
    return jsonify({'user': {
        'email': user.email,
        'name': user.name,
        'address': user.address,
        'sex': user.sex,
        'marital_status': user.marital_status,
        'occupation': user.occupation,
        'country_of_origin': user.country_of_origin,
        'reason': user.joining_reason,
        'phone_number': user.phone_number,
        'dob': user.dob
    }}),200


@api.route('/profile/change-password',methods=['POST'])
@check_token()
def change_password():
    user = g.current_user
    try:
        data = request.get_json()
        oldPass = data['old_password']
        newPass = data['new_password']
        if oldPass is None or newPass is None:
            return jsonify({'errors': { 'form': 'Both old and new password are required'}}), 400
        if user.verify_password(oldPass):
            if newPass == oldPass:
                return jsonify({'errors':{'form': 'New password cannot be the same as old password'}}),400
            if user.phone_number == newPass:
                return jsonify({'errors': {'form': 'New Password cannot be the same as your phone number'}}) 
            user.password = newPass
            db.session.add(user)
            db.session.commit()
            return jsonify({'success':'Password has been updated successful'}), 200            
        else:
            return jsonify({
            'errors': { 'form': 'The old password used is incorrect' }
        }),400
    except Exception as e:
        #TODO: log error to the file
        return jsonify({
       'errors': {'form': 'An internal server error occurred', 'message': e.__str__() }
    }),400

@api.route('/edit-profile',methods=['GET'])
@check_token()
def edit_profile():
    try:
        args = request.args
        attribute = args['attributte']
        value     = args['value']
        print(attribute)
        if isStrEmpty(attribute) or isStrEmpty(value):
            res = jsonify({
            'errors': {
                'content': 'This field is required'
            }
            })
            res.status_code = 400
            return res
        user = g.current_user
        if attribute == 'email':
            user.email = value
        elif attribute == 'name':
            user.name = value
        elif attribute == 'address':
            user.address = value
        elif attribute == 'dob':
            user.dob = value
        elif attribute == 'occupation':
            user.occupation = value
        elif attribute == 'gender':
            user.sex = value
        elif attribute == 'reason':
            user.joining_reason = value
        elif attribute == 'marital_status':
            user.marital_status = value
        elif attribute == 'country_of_origin':
            user.country_of_origin = value
        elif attribute == 'dob':
            user.dob = value
        else:
            res = jsonify({
            'errors':{
                'content': 'Attribute not understood by the server'
            }
            })
            res.status_code = 400
            return res
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': 'Field updated successfully'})
    except Exception as e:
        return jsonify({
            'errors':{
                'content': e.__str__()
            }
        }),400

def get_referee_user(user):
    vol = Volunteer.query.filter_by(tf_id=user.volunteer_ref_id).first()
    if vol.refered_id is None:
        return None
    elif isStrEmpty(vol.refered_id):
        return None
    user = User.query.filter_by(volunteer_ref_id=vol.refered_id).first()
    return user