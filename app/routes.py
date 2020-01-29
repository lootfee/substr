from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db, mail, photos
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Company, Submenu, FoodItem, Orders
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, BecomePartnerForm, EditCompanyForm, AddAdminForm, AddStaffForm, AddSubMenuForm, AddFoodItemForm, EditFoodItemForm, OrderListForm, OrderCheckoutForm
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from oauth import OAuthSignIn
from flask_mail import Message
import json
from sqlalchemy.orm import class_mapper


'''def serialize(model):  for creating json from sqlalchemy
  """Transforms a model into a dictionary which can be dumped to JSON."""
  # first we get the names of all the columns on your model
  columns = [c.key for c in class_mapper(model.__class__).columns]
  # then we return their values in a dict
  return dict((c, getattr(model, c)) for c in columns)'''

@app.route('/api/v1/users/all', methods=['GET', 'POST'])
def users_api():
	users = User.query.all()
	user_list= []
	for u in users:
		user_dict = {"username": u.username}
		user_list.append(user_dict)
	return jsonify(user_list)
	

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	restaurants = Company.query.filter(Company.date_approved.isnot(None), Company.cover_pic.isnot(None)).filter_by(business_type='Restaurant').order_by(Company.name.asc()).all()
	for r in restaurants:
		r.show_order = 0
	for n in range(0, len(restaurants)):
		r.show_order = n
		print(r.show_order)
	become_partner_form = BecomePartnerForm()
	if become_partner_form.validate_on_submit():
		company = Company(name=become_partner_form.business_name.data, business_type=become_partner_form.business_type.data, address=become_partner_form.business_address.data, contact=become_partner_form.contact_info.data, email=become_partner_form.email.data)
		db.session.add(company)
		db.session.commit()
		msg = Message("Substr Partner Request", sender=app.config['MAIL_USERNAME'], recipients=["substr@labapp.tech"])
		msg.html = "<h5>" + become_partner_form.business_name.data  + " is inquiring to be a partner.</h5><p>Business address: " +  become_partner_form.business_address.data  + "</p><p>Email: " +  become_partner_form.email.data + "</p><p>Contact: " +  become_partner_form.contact_info.data  + "</p><p>Message: " + become_partner_form.message.data + "</p>"
		mail.send(msg)
		try:
			mail.send(msg)
		except smtplib.SMTPRecipientsRefused:
			return redirect(url_for('index'))
		except smtplib.SMTPRecipientsRefused:
			return redirect(url_for('index'))
		return redirect(url_for('index'))
	return render_template('index.html', become_partner_form=become_partner_form, restaurants=restaurants)
	
	
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
	if not current_user.is_substr_admin():
		return redirect(url_for('index'))
	pending_requests = Company.query.filter(Company.date_requested.isnot(None)).filter_by(date_approved=None).all()
	partners = Company.query.filter(Company.date_approved.isnot(None)).all()
	return render_template('admin.html', pending_requests=pending_requests, partners=partners)
	

@app.route('/approve_request/<comp_id>')
@login_required
def approve_request(comp_id):
	if not current_user.is_substr_admin():
		return redirect(url_for('index'))
	approved_company = Company.query.filter_by(id=comp_id).first()
	approved_company.date_approved = datetime.utcnow()
	for_hash = approved_company.name + approved_company.date_approved.strftime("%m%d%Y%H%M%S")
	approved_company.set_company_hash(for_hash)
	db.session.commit()
	return redirect(url_for('admin'))
	
@app.route('/reject_request/<comp_id>')
@login_required
def reject_request(comp_id):
	if not current_user.is_substr_admin():
		return redirect(url_for('index'))
	company = Company.query.get(comp_id)
	db.session.delete(company)
	db.session.commit()
	return redirect(url_for('admin'))
	
	
@app.route('/partners/<comp_name>/<comp_hash>', methods=['GET', 'POST'])
def partner(comp_name, comp_hash):
	company = Company.query.filter_by(company_hash=comp_hash).first()
	submenu = Submenu.query.filter_by(company_id=company.id).all()
	for menu in submenu:
		menu.show_order = 0
	for n in range(0, len(submenu)):
		menu.show_order = str(n)
		menu.hash_order = menu.submenu_hash + menu.show_order
	orders_form = OrderListForm()
	if orders_form.validate_on_submit():
		food_id_list = request.form.getlist('order_food_id')
		food_hash_list = request.form.getlist('order_food_hash')
		qty_list = request.form.getlist('order_quantity')
		for i in range(0, len(food_hash_list)):  #dont set price here so it will be updated for future price change before checkout--set price in checkout
			list = Orders(food_item_hash=food_hash_list[i], quantity=qty_list[i], food_item_id=food_id_list[i], user_id=current_user.id, company_id=company.id)
			db.session.add(list)
			db.session.commit()
		return redirect(url_for('checkout', username=current_user.username))
	return render_template('partner.html', company=company, submenu=submenu, orders_form=orders_form)
	
@app.route('/manage_company/<comp_name>/<comp_hash>', methods=['GET', 'POST'])
@login_required
def manage_company(comp_name, comp_hash):
	company = Company.query.filter_by(company_hash=comp_hash).first()
	if not current_user.is_company_admin(company):
		return redirect(url_for('index'))
	edit_comp_form = EditCompanyForm(company.email)
	if edit_comp_form.submit_ecf.data:
		if edit_comp_form.validate_on_submit():
			company.name = edit_comp_form.business_name.data
			company.business_type = edit_comp_form.business_type.data
			company.address = edit_comp_form.business_address.data
			company.contact = edit_comp_form.contact_info.data
			company.email = edit_comp_form.email.data
			company.description = edit_comp_form.company_description.data
			if edit_comp_form.cover_pic.data:
				pic_query = Company.query.filter_by(cover_pic=str(edit_comp_form.cover_pic.data)).first()
				if pic_query is None:
					cover_pic_filename = photos.save(edit_comp_form.cover_pic.data)
					company.cover_pic = photos.url(cover_pic_filename)
				else:
					flash('Duplicate cover pic name, please choose a different(specific) name for your cover pic.')
					return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
			db.session.commit()
			return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
	elif request.method == 'GET':
		edit_comp_form.business_name.data = company.name
		edit_comp_form.business_type.data = company.business_type 
		edit_comp_form.business_address.data = company.address
		edit_comp_form.contact_info.data = company.contact
		edit_comp_form.email.data = company.email
		edit_comp_form.company_description.data = company.description
	add_admin_form = AddAdminForm()
	if add_admin_form.submit_admin_form.data:
		if add_admin_form.validate_on_submit():
			user = User.query.filter_by(username=add_admin_form.input_admin.data).first()
			company.admins.append(user)
			company.staffs.append(user)
			db.session.commit()
			return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
	add_staff_form = AddStaffForm()
	if add_staff_form.submit_staff_form.data:
		if add_staff_form.validate_on_submit():
			user = User.query.filter_by(username=add_staff_form.input_staff.data).first()
			company.staffs.append(user)
			db.session.commit()
			return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
	add_submenu_form = AddSubMenuForm()
	if add_submenu_form.submit_submenu_form.data:
		if add_submenu_form.validate_on_submit():
			submenu = Submenu(name=add_submenu_form.input_submenu.data, description=add_submenu_form.submenu_description.data, company_id=company.id)
			for_hash = submenu.name + str(submenu.id) + str(company.id)
			submenu.set_submenu_hash(for_hash)
			db.session.add(submenu)
			db.session.commit()
			return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
	return render_template('manage_company.html', company=company, edit_comp_form=edit_comp_form, add_admin_form=add_admin_form, add_staff_form=add_staff_form, add_submenu_form=add_submenu_form)
	
	
@app.route('/remove_admin/<comp_hash>/<admin_id>', methods=['GET', 'POST'])
@login_required
def remove_admin(comp_hash, admin_id):
	company = Company.query.filter_by(company_hash=comp_hash).first()
	if not current_user.is_company_admin(company):
		return redirect(url_for('index'))
	user = User.query.filter_by(id=admin_id).first()
	company.admins.remove(user)
	return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
	

@app.route('/remove_staff/<comp_hash>/<staff_id>', methods=['GET', 'POST'])
@login_required
def remove_staff(comp_hash, staff_id):
	company = Company.query.filter_by(company_hash=comp_hash).first()
	if not current_user.is_company_admin(company):
		return redirect(url_for('index'))
	user = User.query.filter_by(id=staff_id).first()
	company.staffs.remove(user)
	return redirect(url_for('manage_company', comp_hash=company.company_hash, comp_name=company.name))
	

	
@app.route('/manage_submenu/<submenu_name>/<submenu_hash>', methods=['GET', 'POST'])
@login_required
def manage_submenu(submenu_name, submenu_hash):
	submenu = Submenu.query.filter_by(submenu_hash=submenu_hash).first()
	foods = FoodItem.query.filter_by(submenu_id=submenu.id).order_by(FoodItem.name.asc()).all()
	company = Company.query.filter_by(id=submenu.company_id).first()
	if not current_user.is_company_admin(company):
		return redirect(url_for('index'))
	edit_submenu_form = AddSubMenuForm()
	if edit_submenu_form.submit_submenu_form.data:
		if edit_submenu_form.validate_on_submit():
			submenu.name = edit_submenu_form.input_submenu.data, 
			submenu.description = edit_submenu_form.submenu_description.data,
			db.session.commit()
			return redirect(url_for('manage_submenu', submenu_name=submenu.name, submenu_hash=submenu.submenu_hash))
	food_item_form = AddFoodItemForm()
	if food_item_form.submit_food_item_form.data:
		if food_item_form.validate_on_submit():
			food_item = FoodItem(name=food_item_form.food_item_name.data, price=food_item_form.food_item_price.data, description=food_item_form.food_item_description.data, company_id=submenu.company_id, submenu_id=submenu.id)
			for_hash = food_item.name + str(food_item.id) + str(submenu.company_id) + str(food_item.price)
			food_item.set_food_item_hash(for_hash)
			if food_item_form.food_item_pic.data:
				pic_query = FoodItem.query.filter_by(cover_pic=str(food_item_form.food_item_pic.data)).first()
				if pic_query is None:
					food_item_pic_filename = photos.save(food_item_form.food_item_pic.data)
					food_item.cover_pic = photos.url(food_item_pic_filename)
				else:
					flash('Duplicate cover pic name, please choose a different(specific) name for your cover pic.')
					return redirect(url_for('manage_submenu', submenu_name=submenu.name, submenu_hash=submenu.submenu_hash))
			db.session.add(food_item)
			db.session.commit()
			return redirect(url_for('manage_submenu', submenu_name=submenu.name, submenu_hash=submenu.submenu_hash))
	edit_food_item_form = EditFoodItemForm()
	food_item_list = [(f.id, f.name) for f in foods]
	edit_food_item_form.edit_food_item_name.choices = food_item_list
	if edit_food_item_form.validate_on_submit():
		edit_food_item = FoodItem.query.filter_by(id=edit_food_item_form.edit_food_item_name.data).first()
		edit_food_item.description = edit_food_item_form.edit_item_description.data
		if edit_food_item_form.edit_food_item_pic.data:
				edit_pic_query = FoodItem.query.filter_by(cover_pic=str(edit_food_item_form.edit_food_item_pic.data)).first()
				if edit_pic_query is None:
					food_item_pic_filename = photos.save(edit_food_item_form.edit_food_item_pic.data)
					edit_food_item.cover_pic = photos.url(food_item_pic_filename)
				else:
					flash('Duplicate cover pic name, please choose a different(specific) name for your cover pic.')
					return redirect(url_for('manage_submenu', submenu_name=submenu.name, submenu_hash=submenu.submenu_hash))
		db.session.commit()
		return redirect(url_for('manage_submenu', submenu_name=submenu.name, submenu_hash=submenu.submenu_hash))
	return render_template('submenu.html', submenu=submenu, edit_submenu_form=edit_submenu_form, food_item_form=food_item_form, foods=foods, edit_food_item_form=edit_food_item_form)
	
	
@app.route('/checkout/<username>', methods=['GET', 'POST'])
@login_required
def checkout(username):
	pending_orders = Orders.query.filter_by(user_id=current_user.id, date_purchased=None).all()
	checkout_form = OrderCheckoutForm()
	if checkout_form.validate_on_submit():
		order_id_list = request.form.getlist('order_id')
		qty_list = request.form.getlist('order_quantity')
		for i in range(0, len(order_id_list)):
			order = Orders.query.filter_by(id=order_id_list[i]).first()
			print(order_id_list[i])
			order.quantity = qty_list[i]
			order.price = order.food_item.price  #set price here so that it will be saved and not be affected by future price change
			order.date_purchased = datetime.utcnow()
			db.session.commit()
		return redirect(url_for('index'))
	return render_template('checkout.html', pending_orders=pending_orders, checkout_form=checkout_form)
	
	
@app.route('/remove_item/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_item():
	item = Order.query.filter_by(id=id).first()
	if not item.is_ordered_by(current_user):
		return redirect(url_for('index'))
	db.session.delete(item)
	db.session.commit()
	return redirect(url_for('checkout', username=current_user.username))