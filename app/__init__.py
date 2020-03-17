from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_uploads import configure_uploads, patch_request_class, UploadSet, IMAGES
from flask_moment import Moment
#from flask_googlemaps import GoogleMaps
#import googlemaps
#from geopy.geocoders import Nominatim
#import gmaps


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app, size=629145)
#gmaps.configure(api_key=os.getenv('GOOGLE_API_KEY'))
#gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))
#google_maps = GoogleMaps(app)
#geolocator = Nominatim()

if not app.debug:
	if app.config['MAIL_SERVER']:
		auth = None
		if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
			auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		secure = None
		if app.config['MAIL_USE_TLS']:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
			fromaddr='no-reply@' + app.config['MAIL_SERVER'],
			toaddrs=app.config['ADMINS'], subject='Substr Failure',
			credentials=auth, secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)

		if not os.path.exists('logs'):
			os.mkdir('logs')
		file_handler = RotatingFileHandler('logs/substr.log', maxBytes=10240,
										   backupCount=10)
		file_handler.setFormatter(logging.Formatter(
			'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)

		app.logger.setLevel(logging.INFO)
		app.logger.info('Substr startup')
		
		
from app import routes, models, errors