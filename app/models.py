from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import hashlib
from time import time
import jwt

admins = db.Table('admins',
	db.Column('admin', db.Integer, db.ForeignKey('user.id')),
	db.Column('company', db.Integer, db.ForeignKey('company.id')),
)

staffs = db.Table('staffs',
	db.Column('staff', db.Integer, db.ForeignKey('user.id')),
	db.Column('company', db.Integer, db.ForeignKey('company.id')),
)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64))
	email = db.Column(db.String(120), index=True, unique=True)
	address = db.Column(db.String(120))
	birthday = db.Column(db.Date)
	social_id = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	profile_pic = db.Column(db.String(1000))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	
	orders = db.relationship('Orders', backref=db.backref('ordered_by', lazy=True), lazy='dynamic')
	#task_requests = db.relationship('TaskRequests', backref=db.backref('requested_by', lazy=True), lazy='dynamic')
	#tasks_performed = db.relationship('TaskRequests', backref=db.backref('fulfilled_by', lazy=True), lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
		
	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)
		
	def is_superadmin(self):
		return self.id == 1
		
	def is_company_admin(self, company):
		return self.admin_of.filter(admins.c.company == company.id).count() > 0 or self.id == 1
		
	def is_company_staff(self, company):
		return self.staff_of.filter(staffs.c.company == company.id).count() > 0 or self.id == 1
		
	def is_substr_admin(self):
		return self.admin_of.filter(admins.c.company == 1).count() > 0 or self.id == 1
		
	def is_substr_staff(self):
		return self.staff_of.filter(staffs.c.company == 1).count() > 0 or self.id == 1
		
	
		
class Company(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	address = db.Column(db.String(128))
	contact = db.Column(db.String(64))
	email = db.Column(db.String(64))
	social_id = db.Column(db.String(64), unique=True)
	business_type = db.Column(db.String(64))
	admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_requested = db.Column(db.DateTime, default=datetime.utcnow)
	date_approved = db.Column(db.DateTime)
	cover_pic = db.Column(db.String(1000))
	description = db.Column(db.String(1000))
	company_hash = db.Column(db.String(128))
	
	submenus = db.relationship('Submenu', backref=db.backref('submenu_of', lazy=True), lazy='dynamic')
	orders = db.relationship('Orders', backref=db.backref('company', lazy=True), lazy='dynamic')
	
	admins = db.relationship(
		'User', secondary='admins',
		backref=db.backref('admin_of', lazy='dynamic'), lazy='dynamic'
	)
	
	staffs = db.relationship(
		'User', secondary='staffs',
		backref=db.backref('staff_of', lazy='dynamic'), lazy='dynamic'
	)
	
	def set_company_hash(self, name):
		self.company_hash = hashlib.sha256(name.encode('utf-8')).hexdigest()
		
		
class Submenu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	description = db.Column(db.String(1000))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	submenu_hash = db.Column(db.String(128))
	
	foods = db.relationship('FoodItem', backref=db.backref('of_submenu', lazy=True), lazy='dynamic')
	
	def set_submenu_hash(self, name):
		self.submenu_hash = hashlib.sha256(name.encode('utf-8')).hexdigest()
		
		
class FoodItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128))
	price = db.Column(db.Numeric(10,2))
	description = db.Column(db.String(1000))
	cover_pic = db.Column(db.String(1000))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	submenu_id = db.Column(db.Integer, db.ForeignKey('submenu.id'))
	food_item_hash = db.Column(db.String(128))
	
	orders = db.relationship('Orders', backref=db.backref('food_item', lazy=True), lazy='dynamic')
	
	def set_food_item_hash(self, name):
		self.food_item_hash = hashlib.sha256(name.encode('utf-8')).hexdigest()
		
		
class Orders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	food_item_hash = db.Column(db.String(128))
	quantity = db.Column(db.String(16))
	price = db.Column(db.Numeric(10,2))
	date_purchased = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'))
	
	def is_ordered_by(self, user):
		return self.ordered_by == user
		

class TaskRequests(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	from_address = db.Column(db.String(200))
	to_address = db.Column(db.String(200))
	description = db.Column(db.String(2000))
	date_requested = db.Column(db.DateTime)
	date_completed = db.Column(db.DateTime)
	
	requested_by = db.relationship('User', backref=db.backref('task_request', lazy=True), foreign_keys=[requester_id])
	fulfilled_by = db.relationship('User', backref=db.backref('task_performed', lazy=True), foreign_keys=[driver_id])