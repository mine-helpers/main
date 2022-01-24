from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import admin
from .forms import EditProfileAdminForm, PackageForm, VolunteerForm, \
 SettingsEditForm, SettingsForm, AmendAccountToMerchantForm, SearchPhoneForm
from .. import db
from ..models import Permission, Role, Admin, Account, Package, Volunteer, \
 PaymentCollection, Voucher, Transaction, User, Setting, AccountType
from ..decorators import admin_required, permission_required
from ..airtime import DonationTime
from app.api_1_0.validation import isStrEmpty
from sqlalchemy import func
from ..auth.forms import RegistrationForm

@admin.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['KEFA_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response

@admin.route('/',methods=['GET'])
@login_required
@admin_required
def index():
    users_count = User.query.count()
    transactions_count = Transaction.query.count()
    acc = Account.get_balance()
    bal = acc[0]
    vsse = acc[1]
    payment = PaymentCollection.get_balance()
    return render_template('admin/index.html',users_count=users_count,
 transactions_count=transactions_count, bal=bal,vsse=vsse,payment=payment)

@admin.route('/search',methods=['GET','POST'])
@login_required
@admin_required
def search_phone():
    form = SearchPhoneForm()
    if form.validate_on_submit():
        phone = form.phone.data
        user = User.query.filter_by(phone_number=phone).first()
        form = SearchPhoneForm()
        return render_template('admin/search.html',user=user,form=form)
    return render_template('admin/search.html',user=None,form=form)


@admin.route('/packages',methods=['GET','POST'])
@login_required
@admin_required
def packages():
    packages = Package.query.all()
    return render_template('admin/packages.html',packages=packages)

@admin.route('/package/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def package(id):
    package = Package.query.get(id)
    batches = db.session.query(Voucher.voucher_set_id,func.count(Voucher.id)).filter(Voucher.package_id==id).group_by(Voucher.voucher_set_id).all()

    if request.method =='POST':
        #generate vouchers for this package 
        #create a batch code
        donation = DonationTime()
        batch_id = create_batch_id(id)
        for _ in range(100):
            voucher_code = donation.getImei(14)
            #save the voucher on the package
            voucher = Voucher(package=package,voucher_set_id=batch_id,code=voucher_code,is_active=True)
            db.session.add(voucher)
            db.session.commit()
        flash('Donation time voucher codes have been generated successfully')
        return redirect(url_for('.package',id=package.id))
    return render_template('admin/voucher_batches.html',batches=batches,package=package)

@admin.route('/package/<int:id>/batch/<int:batch_id>',methods=['GET'])
@login_required
@admin_required
def voucher_batch(id,batch_id):
    package =  Package.query.get(id)
    batch_package_vouchers = db.session.query(Voucher).filter(Voucher.package_id==id).filter(Voucher.voucher_set_id==batch_id)
    active_vouchers = batch_package_vouchers.filter(Voucher.is_active==True).all()
    inactive_vouchers = batch_package_vouchers.filter(Voucher.is_active==False).all()
    return render_template('admin/package.html',package=package,
                       active_vouchers=active_vouchers,inactive_vouchers=inactive_vouchers)

@admin.route('/package/new',methods=['GET','POST'])
@login_required
@admin_required
def new_package():
    form = PackageForm()
    if form.validate_on_submit():
        package = Package(name=form.name.data,amount=form.amount.data)
        db.session.add(package)
        db.session.commit()
        flash("New Package has been created successfully!")
        return redirect(url_for('.packages'))
    return render_template('admin/new_package.html',form=form)


@admin.route('/new/volunteer',methods=['GET','POST'])
@login_required
def new_volunteer():
    form =  VolunteerForm()
    if form.validate_on_submit():
        tf_id = createVolunteerId()

        if isStrEmpty(form.refered_by.data):
            volunteer = Volunteer(name=form.name.data,phone_number=form.phone_number.data,tf_id=tf_id)
            db.session.add(volunteer)
        else:
            v = Volunteer.query.filter_by(tf_id=form.refered_by.data).first()
            if v is None:
                flash('Unknown volunteer reference id')
                return render_template('admin/new_volunteer.html',form=form)

            volunteer = Volunteer(name=form.name.data,phone_number=form.phone_number.data,
                                   refered_id=v.tf_id,tf_id=tf_id)
            db.session.add(volunteer)

        db.session.commit()
        flash('Volunteer has been added successfully.')
        return redirect(url_for('.volunteers'))
    return render_template('admin/new_volunteer.html',form=form)

@admin.route('/volunteers',methods=['GET'])
@login_required
@admin_required
def volunteers():
    volunteers = Volunteer.query.all()
    return render_template('admin/volunteers.html',volunteers=volunteers)

@admin.route('/volunteer/<int:id>/delete',methods=['GET'])
@login_required
@admin_required
def delete_volunteer(id):
    volunteer = Volunteer.query.get(id)
    db.session.remove(volunteer)
    flash('Volunteer has been successfully.')
    return redirect(url_for('.volunteers'))


def createVolunteerId():
    tf_id = ''
    vol = db.session.query(Volunteer).order_by(Volunteer.id.desc()).first()
    if vol is not None:
        ref_id = vol.id + 1
        tf_id = 'TF00{0}'.format(ref_id)
    else:
        tf_id = 'TF001'

    return tf_id

def create_batch_id(package_id):
    batch_id = 1
    v = db.session.query(Voucher).filter(Voucher.package_id==package_id).order_by(Voucher.id.desc()).first()
    if v is not None:
        batch_id = v.voucher_set_id + 1
    return batch_id


@admin.route('/setting/new',methods=['GET','POST'])
@login_required
@admin_required
def add_setting():
    form = SettingsForm()
    if form.validate_on_submit():
        setting = Setting(name=form.name.data,value=form.value.data)
        db.session.add(setting)
        db.session.commit()
        flash("New Setting has been created successfully!")
        return redirect(url_for('.settings'))
    return render_template('admin/new_setting.html',form=form)

@admin.route('/setting/<int:id>/edit',methods=['GET','POST'])
@login_required
@admin_required
def edit_setting(id):
    setting = Setting.query.get_or_404(id)
    form = SettingsEditForm(setting)
    if form.validate_on_submit():
        setting.value = form.value.data
        db.session.add(setting)
        db.session.commit()
        flash("New Setting has been editted successfully!")
        return redirect(url_for('.settings'))
    form.value.data = setting.value
    return render_template('admin/edit_setting.html',form=form,setting=setting)

@admin.route('/settings',methods=['GET','POST'])
@login_required
@admin_required
def settings():
    ss = Setting.query.all()
    return render_template('admin/settings.html',ss=ss)

@admin.route('/create-user',methods=['GET','POST'])
@login_required
@admin_required
def add_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        merchant = Admin(
            username = form.username.data,
            phone_number = form.phone_number.data,
            email = form.email.data,
            password = form.password.data,
            name = form.name.data
        )      
        role = Role.query.filter_by(name='Moderator').first()
        merchant.role = role
        db.session.add(merchant)
        db.session.commit()
        flash("Merchant added succesfully")
        return redirect(url_for('.merchants'))
    return render_template('admin/merchants/add.html',form=form)

@admin.route('/create-merchant',methods=['GET','POST'])
@login_required
@admin_required
def create_merchant():
    form = AmendAccountToMerchantForm()
    if form.validate_on_submit():
        merchant = Admin(
            username = form.username.data,
            phone_number = form.phone_number.data,
            email = form.email.data,
            password = form.password.data,
            name = form.name.data
        )      
        role = Role.query.filter_by(name='Moderator').first()
        merchant.role = role
        db.session.add(merchant)
        db.session.commit()
        flash("Merchant added succesfully")
        return redirect(url_for('.merchants'))
    return render_template('admin/merchants/add.html',form=form)

@admin.route('/merchants',methods=['GET','POST'])
@login_required
@admin_required
def merchants():
    accType = AccountType.query.filter_by(default=True).first()
    ms = Account.query.filter(Account.account_type!=accType).all()
    return render_template('admin/merchants/merchants.html',merchants=ms)

@admin.route('/account/<int:id>/amend',methods=['GET','POST'])
@login_required
@admin_required
def amend_account(id):
    account = Account.query.filter_by(id=id).first()
    if account:
        account_type = AccountType.query.filter_by(name='Merchant').first()
        account.account_type = account_type
        db.session.add(account)
        db.session.commit()
        flash('Account ammended to a merchant account successfully')
        return redirect(url_for('admin.merchants'))
    flash('Account failed to be ammended to a merchant account successfully')
    return redirect(url_for('admin.search_phone'))

@admin.route('/default-accounts',methods=['GET'])
def default_all_accounts():
    accounts = Account.query.all()
    account_type = AccountType.query.filter_by(name='User').first()
    for account in accounts:
        account.account_type = account_type
        db.session.add(account)
        db.session.commit()
    return jsonify({'status': 'All changed successfully'})
