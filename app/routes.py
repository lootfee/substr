from flask import render_template, flash, redirect, url_for, request
from app import app, db, mail
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, BecomePartnerForm
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from oauth import OAuthSignIn
from flask_mail import Message


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
	become_partner_form = BecomePartnerForm()
	if become_partner_form.validate_on_submit():
		company = Company(name=become_partner_form.business_name.data, address=become_partner_form.business_address.data, contact=become_partner_form.contact_info.data, email=become_partner_form.email.data)
		db.session.add(company)
		db.session.commit()
		msg = Message("Substr Partner Request", sender="support@labapp.tech", recipients=["support@labapp.tech"])
		msg.html = "<h5>" + become_partner_form.business_name.data  + " is inquiring to be a partner.</h5><p>Business address: " +  become_partner_form.business_address.data  + "</p><p>Email: " +  become_partner_form.email.data + "</p><p>Contact: " +  become_partner_form.contact_info.data  + "</p><p>Message: " + become_partner_form.message.data + "</p>"
		mail.send(msg)
		return redirect(url_for('index'))
	return render_template('index.html', become_partner_form=become_partner_form)
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)



@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		user = User(social_id=social_id, username=username, email=email)
		db.session.add(user)
		db.session.commit()
	login_user(user, True)
	return redirect(url_for('index'))
	
	
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
	
	
@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')
	
	
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
	
	
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
						   
						   
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html', title='Reset Password', form=form)
	

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
	
	
	
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
	return render_template('user.html')
	
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	return render_template('admin.html')