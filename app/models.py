from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    USER = 0x01
    MERCHANT = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    admins = db.relationship('Admin', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'USER': (Permission.USER,True),
            'Moderator': (Permission.USER |
                          Permission.MERCHANT,False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    phone_number = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['KEFA_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<Admin %r>' % self.username


class AnonymousAdmin(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousAdmin


@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))


class NextOfKin(db.Model):
    __tablename__ = 'next_of_kins'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256),index=True,nullable=False)
    related = db.Column(db.String(256),nullable=False)
    address = db.Column(db.String(256))
    country_of_origin = db.Column(db.String(100))
    telephone = db.Column(db.String(100),nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    user = db.relationship('User', backref='next_of_kin',uselist=False)

class Login(db.Model):
    __tablename__ = 'logins'
    id = db.Column(db.Integer,primary_key=True)
    ip_address = db.Column(db.String(64),nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    phone_number = db.Column(db.String(64), unique=True, index=True,nullable=False)
    volunteer_ref_id = db.Column(db.String(64),nullable=False)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    address = db.Column(db.String(64))
    sex = db.Column(db.String(100))
    marital_status = db.Column(db.String(100))
    dob = db.Column(db.Date())
    occupation = db.Column(db.String(100))
    country_of_origin = db.Column(db.String(100))
    joining_reason = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    next_of_kin_id = db.Column(db.Integer, db.ForeignKey('next_of_kins.id'))
    account = db.relationship('Account', backref='owner',uselist=False)
    logins = db.relationship('Login', backref='user', lazy='dynamic')
    payment_collections = db.relationship('PaymentCollection', backref='payer', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def to_json(self):
        json_user = {
                'id': self.id,
                'phoneNumber': self.phone_number,
                'volunteerId': self.volunteer_ref_id,
                'confirmed': self.confirmed,
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id,'accountNumber': self.account.account_number,
        'accountBalance':self.account.account_balance, 'goalBalance': self.account.goals_balance,
        'phoneNumber':self.phone_number,'kfp_type': self.account.account_type.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.phone_number

class AccountType(db.Model):
    __tablename__ = 'account_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    accounts = db.relationship('Account', backref='account_type', lazy='dynamic')

    @staticmethod
    def insert_types():
        types = {
            'User': (Permission.USER,True),
            'Merchant': (Permission.USER |
                          Permission.MERCHANT,False)
        }
        for r in types:
            accType = AccountType.query.filter_by(name=r).first()
            if accType is None:
                accType = AccountType(name=r)
            accType.permissions = types[r][0]
            accType.default = types[r][1]
            db.session.add(accType)
        db.session.commit()

    def __repr__(self):
        return '<AccountType %r>' % self.name

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(100),nullable=False,unique=True)
    account_balance = db.Column(db.Float,default=0.0)
    goals_balance   = db.Column(db.Float,default=0.0)
    vsse_balance   = db.Column(db.Float,default=0.0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_type_id = db.Column(db.Integer, db.ForeignKey('account_types.id'))
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
        self.accountType = AccountType.query.filter_by(default=True).first()

    @staticmethod
    def get_balance():
        bal = 0
        vsse = 0
        accs = Account.query.all()
        for acc in accs:
            bal = bal + acc.account_balance
            vsse = vsse + acc.vsse_balance
        return bal,vsse

    def to_json(self):
        json_account = {
            'id': self.id,
            'accountNumber': self.account_number,
            'accountBalance': self.account_balance,
            'goalsBalance': self.goals_balance,
            'vsseBalance': self.vsse_balance,
            'phoneNumber': self.owner.phone_number,
            'timestamp': self.timestamp,
            'account_type': {
                'name': self.account_type.name,
                'id': self.account_type.id
            }
        }
        return json_account

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer,primary_key=True)
    amount = db.Column(db.Float,nullable=False)
    transaction_type = db.Column(db.String(200),nullable=False)
    transaction_status = db.Column(db.String(200),nullable=False)
    account_id = db.Column(db.Integer,db.ForeignKey('accounts.id'))
    reason = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)

    def to_json(self):
        json_transaction = {
            'id': self.id,
            'amount': self.amount,
            'transactionType': self.transaction_type,
            'reason': self.reason,
            'timestamp': self.timestamp.strftime('%d, %b %Y')
        }  
        return json_transaction      

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    error = db.Column(db.Text)
    error_code = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True,default=datetime.utcnow) 

    def to_json(self):
        json_log = {
            'returned_body': self.body,
            'error': self.error,
        }
        return json_log

class Message(db.Model):
    __tablename__ ='messages'
    id = db.Column(db.Integer,primary_key=True)
    phone_number = db.Column(db.String(100))
    body = db.Column(db.Text)
    status = db.Column(db.String(100))
    delivery_status = db.Column(db.String(100))
    status_code = db.Column(db.Integer)
    unique_id = db.Column(db.String(100),unique=True,index=True)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__='notifications'
    id = db.Column(db.Integer,primary_key=True)
    amount = db.Column(db.Float)
    phone_number = db.Column(db.String(100))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(100))
    last_error = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_json(self):
        json_note = {
            'id': self.id,
            'amount': self.amount,
            'phone_number': self.phone_number,
            'reason': self.reason,
            'status': self.status,
            'last_error': self.last_error,
        }
        return json_note
class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    amount = db.Column(db.Float,nullable=False)
    payment_collections = db.relationship('PaymentCollection', backref='package', lazy='dynamic')
    vouchers = db.relationship('Voucher', backref='package', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def get_total_revenue(self):
        total_revenue = 0
        for col in self.payment_collections:
            total_revenue = total_revenue + col.amount
        return total_revenue

    def dispatched_vouchers(self):
        count = db.session.query(Voucher).filter(Voucher.package_id==self.id).filter(Voucher.is_active == False).count()
        return count

    def available_vouchers(self):
        count = db.session.query(Voucher).filter(Voucher.package_id==self.id).filter(Voucher.is_active == True).count()
        return count
        

    def to_json(self):
        json_package = {
          'id': self.id,
          'amount': self.amount,
          'timestamp': self.timestamp
        }
        return json_package
class Voucher(db.Model):
    __tablename__ = 'vouchers'
    id = db.Column(db.Integer, primary_key=True)
    voucher_set_id = db.Column(db.Integer)
    code = db.Column(db.String(100), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True,index=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    payment_collection = db.relationship('PaymentCollection', backref='voucher', uselist=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    @staticmethod
    def get_available_vouchers():
        count = db.session.query(Voucher).filter(Voucher.is_active==True).count()
        return count

    @staticmethod
    def get_sold_vouchers():
        count = db.session.query(Voucher).filter(Voucher.is_active==False).count()
        return count

    @staticmethod
    def get_active_voucher_by_package(package):
        voucher = Voucher.query.filter(Voucher.package_id==package.id).filter(Voucher.is_active==True).first()
        return voucher


    def to_json(self):
        json_voucher = {
            'id': self.id,
            'code': self.code,
            'timestamp': self.timestamp
        }
        return json_voucher
class PaymentCollection(db.Model):
    __tablename__='payment_collections'
    id = db.Column(db.Integer,primary_key=True)
    pay_id = db.Column(db.Integer,unique=True,nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'))
    amount = db.Column(db.Float,nullable=False)
    voucher_code = db.Column(db.String,nullable=False)
    voucher_id = db.Column(db.Integer,db.ForeignKey('vouchers.id'))
    timestamp = db.Column(db.DateTime, index=True)

    @staticmethod
    def get_balance():
        cols = PaymentCollection.query.all()
        bal = 0
        for col in cols:
            bal = bal + col.amount
        return bal

    def to_json(self):
        return {
        'id': self.id,
        'user': self.payer.phone_number,
        'package': self.package.name,
        'amount': self.amount,
        'voucher_code': self.voucher_code,
        'timestamp': self.timestamp
    }

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256))
    tf_id = db.Column(db.String(256),unique=True,nullable=False)
    refered_id = db.Column(db.String(256),nullable=True)
    phone_number = db.Column(db.String(14),unique=True,nullable=False)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.now)

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256),nullable=False,index=True)
    value = db.Column(db.String(256),nullable=False)
    created = db.Column(db.DateTime,index=True,default=datetime.now)

    @staticmethod
    def get_setting_by_name(name):
        se = Setting.query.filter_by(name=name).first()
        return se

    def to_json(self):
        json_setting ={
            'name': self.name,
            'value': self.value
        }
        return json_setting