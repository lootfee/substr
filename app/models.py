from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import hashlib

admins = db.Table('admins',
	db.Column('user', db.Integer, db.ForeignKey('user.id')),
	db.Column('company', db.Integer, db.ForeignKey('company.id')),
)

staffs = db.Table('staffs',
	db.Column('user', db.Integer, db.ForeignKey('user.id')),
	db.Column('company', db.Integer, db.ForeignKey('company.id')),
)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	social_id = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	profile_pic = db.Column(db.String(1000))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)

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
		
	def is_company_admin(self, company):
		return self.admin_of.filter(admins.c.company == company.id).count() > 0
		
	def is_company_staff(self, company):
		return self.staff_of.filter(staffs.c.company == company.id).count() > 0
		
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