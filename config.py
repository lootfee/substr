import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__) )
load_dotenv()

class Config(object):
	SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.getenv('MAIL_SERVER')
	MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.getenv('MAIL_USERNAME')
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	ADMINS = os.getenv('ADMINS')
	OAUTH_CREDENTIALS = {
		'facebook': {
			'id': os.getenv('FACEBOOK_TEST_ID'),
			'secret': os.getenv('FACEBOOK_TEST_SECRET')
		},
		'twitter': {
			'id': os.getenv('TWITTER_ID'),
			'secret': os.getenv('TWITTER_SECRET')
		}
	}
	LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT')
	UPLOADED_PHOTOS_DEST = os.getcwd() + '/app/static/uploads'