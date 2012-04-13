from smtplib import SMTPException

from flask import (Blueprint, render_template, abort, request, url_for,
                    flash, redirect, make_response)
from flask.ext.mail import Mail, Message
from itsdangerous import URLSafeSerializer

from . import app
from . import models
from . import utils

mail = Mail(app)

def send_message(id):
    message = models.Message.get(id)
    email = Message("[CARA-RT] Request #%s"%message.ticket_id)
    email.html = render_template('email/message.html', message=message,
                             referrer=utils.serializer.dumps(message.ticket.id))
    email.add_recipient(message.ticket.user.email)
    try:
        mail.send(email)
    except SMTPException as error:
        app.logger.warning("SMTP Error\n%s"%error)

def send_confirmation(id):
    ticket = models.Ticket.get(id)
    email = Message("[CARA-RT] Request #%s"%ticket.id)
    email.html = render_template('email/confirmation.html', message=message,
                             referrer=utils.serializer.dumps(message.ticket.id))
    email.add_recipient(message.ticket.user.email)
    try:
        mail.send(email)
    except SMTPException as error:
        app.logger.warning("SMTP Error\n%s"%error)
    
