from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

admins = db.Table('admins',
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
		
class Company(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	address = db.Column(db.String(128))
	contact = db.Column(db.String(64))
	email = db.Column(db.String(64), unique=True)
	social_id = db.Column(db.String(64), unique=True)
	business_type = db.Column(db.String(64))
	admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_requested = db.Column(db.DateTime, default=datetime.utcnow)
	date_approved = db.Column(db.DateTime)
	
	admins = db.relationship(
		'User', secondary='admins',
		backref=db.backref('company', lazy='dynamic'), lazy='dynamic'
	)