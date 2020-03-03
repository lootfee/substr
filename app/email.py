from flask import render_template
from flask_mail import Message
from app import app, mail
import os

def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    #msg.body = text_body
    msg.html = html_body
    mail.send(msg)
	
	
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Substr] Reset Your Password',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               #text_body=render_template('email/reset_password.txt',
               #                          user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
										 
										 

def send_approve_partner_email(company):
	send_email("Welcome to Substr",
	sender=app.config['MAIL_USERNAME'],
	recipients=[company.email],
	html_body=render_template('email/approve_partner.html', company=company))