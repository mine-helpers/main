from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, FloatField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User, Volunteer, Setting


class PackageForm(FlaskForm):
    name = StringField('Name', validators=[Required()])
    amount = FloatField('Amount',validators=[Required()])
    submit = SubmitField('Create')


class SearchPhoneForm(FlaskForm):
    phone = StringField("Phone Number",validators=[Required()])
    submit = SubmitField("Look Up")

class SettingsForm(FlaskForm):
    name = StringField('Name', validators=[Required()])
    value = StringField('Value',validators=[Required()])
    submit = SubmitField('Save')

    def validate_name(self,field):
        if Setting.query.filter_by(name=field.data).first():
            raise ValidationError("Setting with such name already exists")

class SettingsEditForm(FlaskForm):
    value = StringField('Value',validators=[Required()])
    submit = SubmitField('Save')
    
    def __init__(self, setting, *args, **kwargs):
        super(SettingsEditForm, self).__init__(*args, **kwargs)
        self.setting = setting


class VolunteerForm(FlaskForm):
    phone_number = StringField('Phone Number',validators=[Required(),Length(1,64)])
    name  = StringField('Full Name',validators=[Required()])
    refered_by = StringField('Refered By')
    submit = SubmitField('Submit')

    def validate_phone_number(self,field):
        if Volunteer.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already in use')
    """
    def validate_refered_by(self,field):
        if field.data is not None:
            code = Volunteer.query.filter_by(refered_id=field.data).first()
            if code is None:
                raise ValidationError('Unknown referee volunteer id')
    """

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Name', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class AmendAccountToMerchantForm(FlaskForm):
    account_type = SelectField('Account Type', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, account, *args, **kwargs):
        super(AmendAccountToMerchantForm, self).__init__(*args, **kwargs)
        self.account_type.choices = [(accType.id, accType.name)
                             for accType in AccountType.query.order_by(AccountType.name).all()]
        self.account = account
