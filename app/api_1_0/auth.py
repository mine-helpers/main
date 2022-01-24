from flask import g, jsonify, request
from flask_login import login_user
from ..models import User, Account, Login as UserLoign, Volunteer, AccountType
from . import api
from .errors import unauthorized, forbidden
from sqlalchemy import or_
from .. import db
import uuid
from .decorators import check_token
from .validation import verify_phonenumber, verify_code
import onetimepass as otp
from ..api import kfp_otp
from ..sms import SMSApi


def isEmpty(errors):
    if not errors:
        return True
    raise ValueError('errors must be a dictionary')


def isStrEmpty(param):
    if not param.strip():
        return True
    return False


@api.route('/auth', methods=['POST'])
def login():
    errors = {}
    data = request.get_json()
    username = data['identifier']
    password = data['password']
    if username is None or isStrEmpty(username):
        errors['identifier'] = 'This field is required'
    if password is None or isStrEmpty(password):
        errors['password'] = 'This field is required'
    if not isEmpty(errors):
        res = jsonify({
            'errors': errors
        })
        res.status_code = 400
        return res

    user = db.session.query(User).filter(
        User.phone_number.like(username)).first()
    if user is not None and user.verify_password(password):
        token = user.generate_auth_token(100000000)
        ip = request.remote_addr
        user_login = UserLoign(user=user, ip_address=ip)
        db.session.add(user_login)
        db.session.commit()
        return jsonify({
            'token': token,
            'account_type': user.account.account_type.id,
            'phoneNumber': user.phone_number,
            'id':  user.id
        }), 200
    res = jsonify({
        'errors': {
            'form': 'Wrong username or password'
        }
    })
    res.status_code = 400
    return res


@api.route('/create-account', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        errors = {}
        result = request.get_json()
        #code = result['code']
        volunteer_id = result["volunteerId"]
        phone_number = result["phoneNumber"]
        password = result['password']
        # if code is None or isStrEmpty(code):
        #errors['code'] = 'This field is required'
        # if not verify_code(code):
        #errors['code'] = 'Code is invalid'

        # if code is not None or not isStrEmpty(code) and verify_code(code) and verify_phonenumber(phone_number):
        #otp = kfp_otp()
        # if not otp.verify_otp(int(code),int(phone_number)):
        #errors['code'] = 'Code is invalid. Try registering again'

        if volunteer_id is None or isStrEmpty(volunteer_id):
            errors['volunteerId'] = 'This field is required'
        if phone_number is None or isStrEmpty(phone_number):
            errors['phoneNumber'] = 'This field is required'
        if password is None or isStrEmpty(password):
            errors['password'] = 'This field is required'

        v = Volunteer.query.filter_by(tf_id=volunteer_id).first()
        if v is None:
            errors['volunteerId'] = 'Invalid volunteer id. Register at Kefa Foundation to get a volunteer Id'

        user = db.session.query(User).filter(or_(User.phone_number.like(phone_number),
                                                 User.volunteer_ref_id.like(
                                                     volunteer_id)
                                                 )).first()
        if user is not None:
            if user.phone_number == phone_number:
                errors['phoneNumber'] = 'This phone number is already in use'
            if user.volunteer_ref_id == volunteer_id:
                errors['volunteerId'] = 'This volunteer Id is already in use'

        if not isEmpty(errors):
            return jsonify({
                'errors': errors
            }), 400

        user = User(volunteer_ref_id=volunteer_id,
                    phone_number=phone_number, password=password)
        db.session.add(user)
        db.session.commit()

        # TODO: improve account number creation.
        acc = uuid.uuid4()
        account_number = 'WA{0}'.format(acc.__hash__())

        user.confirmed = True
        account_type = AccountType.query.filter_by(
            name='User').first()  # Get User account #TODO remove Id
        account = Account(
            owner=user, account_number=account_number, account_type=account_type)
        db.session.add(account)
        db.session.add(user)
        db.session.commit()

        return jsonify(
            user.to_json()
        ), 201
    else:
        return jsonify({
            'errors': {
                'form': 'Method not allowed,shame on you!!'
            }
        }), 422


@api.route('/activate-account', methods=['POST'])
@check_token()
def activate_account():
    errors = {}
    result = request.get_json()
    code = result['code']
    if code is None or isStrEmpty(code):
        errors['code'] = 'This field is required'
    if not isEmpty(errors):
        return jsonify({
            'errors': errors
        }), 400
    # TODO: verify that code is valid and generate the account number

    return jsonify({}), 200


@api.route('/check-user/<identifier>', methods=['GET'])
def check_user_exists(identifier):
    user = db.session.query(User).filter(or_(User.phone_number.like(
        identifier), User.volunteer_ref_id.like(identifier))).first()
    if user is not None:
        return jsonify(
            {
                'user': user.to_json()
            }), 400
    else:
        return jsonify({'status': 'successful'})


@api.route('/send-confirmationcode/<identifier>', methods=['GET'])
def send_code(identifier):
    if not verify_phonenumber(identifier):
        return jsonify({'error': 'This phone number is invalid'}), 400
    otp = kfp_otp()
    code = otp.generate_otp(int(identifier))
    sms = SMSApi()
    message = 'This is a test message {0}'.format(code)
    status_code = sms.send_sms(identifier, message)
    if status_code is not 200:
        return jsonify({'error': 'Message could not be sent to this phone number'}), 400
    return jsonify({'identifier': identifier}), 200
