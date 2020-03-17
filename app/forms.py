from flask_wtf import FlaskForm
from app import app, photos
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, FloatField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, InputRequired
from app.models import User, Company
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
	#username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit_login = SubmitField('Sign In')
	
class RegistrationForm(FlaskForm):
	username = StringField('Full name', validators=[DataRequired(), Length(min=4, max=15)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	contact_info = StringField('Contact number', validators=[DataRequired()], default="+639")
	address = StringField('Address', validators=[DataRequired()])
	birthday = DateField('Birthday', validators=[DataRequired()], format='%Y-%m-%d')
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	'''def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')'''

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')
			
class EditProfileForm(FlaskForm):
	username = StringField('Full name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Submit')

	def __init__(self, original_email, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		#self.original_username = original_username
		self.original_email = original_email

	'''def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')'''
				
	def validate_email(self, email):
		if email.data != self.original_email:
			user = User.query.filter_by(email=self.email.data).first()
			if user is not None:
				raise ValidationError('Email is already registered!')
				
				
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
	
	
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
	

class BecomePartnerForm(FlaskForm):
	business_name = StringField('Business name', validators=[DataRequired()])
	business_type = SelectField('Business type', choices=[('Restaurant', 'Restaurant'), ('Retailer', 'Retailer')])
	business_address = StringField('Business address', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	contact_info = StringField('Contact number', validators=[DataRequired()], default="+639")
	message = TextAreaField('Business details', validators=[DataRequired()])
	submit_bpf = SubmitField('Submit')
	
	def validate_email(self, email):
		company = Company.query.filter_by(email=email.data).first()
		if company is not None:
			raise ValidationError('The email has already been registered by another company.')	
			

class EditCompanyForm(FlaskForm):
	business_name = StringField('Business name', validators=[DataRequired()])
	business_type = SelectField('Business type', choices=[('Restaurant', 'Restaurant'), ('Retailer', 'Retailer')])
	business_address = StringField('Business address', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	contact_info = StringField('Contact number', validators=[DataRequired()])
	cover_pic = FileField('Upload Cover Pic (50 kB max size):', validators=[FileAllowed(photos)])
	company_description = TextAreaField('Company description', validators=[DataRequired()])
	submit_ecf = SubmitField('Submit')
	
	def __init__(self, original_email, *args, **kwargs):
		super(EditCompanyForm, self).__init__(*args, **kwargs)
		self.original_email = original_email
		
	def validate_email(self, email):
		if email.data != self.original_email:
			company = Company.query.filter_by(email=self.email.data).first()
			if company is not None:
				raise ValidationError('Email is already registered by a different company!')
				

class AddAdminForm(FlaskForm):
	input_admin = StringField('Add admins', validators=[DataRequired()])
	submit_admin_form = SubmitField('Submit')
	
	
class AddStaffForm(FlaskForm):
	input_staff = StringField('Add staffs', validators=[DataRequired()])
	submit_staff_form = SubmitField('Submit')
	

class AddSubMenuForm(FlaskForm):
	input_submenu = StringField('Add submenu', validators=[DataRequired()], render_kw={"placeholder": "e.g. Breakfast Menu, Lunch Menu, Chicken Menu"})
	submenu_description = TextAreaField('Description', validators=[DataRequired()])
	submit_submenu_form = SubmitField('Submit')
	
	
class AddFoodItemForm(FlaskForm):
	food_item_name = StringField('Name', validators=[DataRequired()])
	food_item_price = FloatField('Price', validators=[DataRequired()])
	food_item_description = TextAreaField('Description', validators=[DataRequired(), Length(max=100)])
	food_item_pic = FileField('Picture (20 kB max size):', validators=[FileAllowed(photos)])
	submit_food_item_form = SubmitField('Submit')
	
class EditFoodItemForm(FlaskForm):
	edit_food_item_name = SelectField('Name', coerce=int, validators=[InputRequired()])
	edit_item_description = TextAreaField('Description', validators=[DataRequired()])
	edit_food_item_pic = FileField('Picture (20 kB max size):', validators=[FileAllowed(photos)])
	submit_edit_item_form = SubmitField('Submit')
	
	
class OrderListForm(FlaskForm):
	order_food_id = HiddenField('food_item_id')
	order_food_hash = HiddenField('food_item_hash')
	order_quantity = HiddenField('qty')
	order_submit = SubmitField('Checkout')
	
class OrderCheckoutForm(FlaskForm):
	order_id = HiddenField('order_id')
	order_quantity = HiddenField('qty')
	checkout_submit = SubmitField('Checkout')
	
	

class TaskRequestForm(FlaskForm):
	task_type = SelectField('Task type', choices=[('Purchase', 'Purchase'), ('Pickup', 'Pickup'), ('Proxy', 'Proxy')])
	address_from = StringField('From', validators=[DataRequired()])
	address_to = StringField('To', validators=[DataRequired()])
	task_description = TextAreaField('Description', validators=[DataRequired(), Length(max=100)])
	submit_task_form = SubmitField('Submit')