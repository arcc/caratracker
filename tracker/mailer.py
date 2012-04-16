"""
Module provides an interface to the system's sendmail client.

It's based heavily off of Flask-Mail (originaly by danjac),
and owes a majority of its code to him.

"""
from flask import _request_ctx_stack

from email.mime.text import MIMEText
from subprocess import PIPE,STDOUT,Popen

class Mailer(object):

    def __init__(self,app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initializes your mail settings from app.config

        Can be used to set up the Mailer at configuration time

        :param app: Flask application instance
        """

        self.debug = app.config.get('MAIL_DEBUG',app.debug)
        self.mailer = app.config.get('MAIL_MAILER','/usr/sbin/sendmail')
        self.mailer_flags = app.config.get('MAIL_MAILER_FLAGS','-t')
        self.suppress = app.config.get('MAIL_SUPPRESS_SEND', False)
        self.fail_silently = app.config.get('MAIL_FAIL_SILENTLY', True)

        self.suppress = self.suppress or app.testing
        self.app = app

        #register extenshion with app
        #app.extensions = getattr(app, 'extensions', {})
        #app.extensions['mail'] = self

    def send(self,message):
        """
        Sends message through system's sendmail client.

        :param message: Mailer Message instance
        """

        if not self.suppress:
            sm = Popen([self.mailer,self.mailer_flags], stdin=PIPE, stdout=PIPE,
                        stderr=STDOUT)
            sm.stdin.write(message.dump())
            sm.communicate()
            
            return sm.returncode
        else:
            
            return True
            
            

class Message(object):
    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **DEFAULT_MAIL_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    """
    def __init__(self, subject, recipients=None, body=None, html=None,
                sender=None, cc=None, bcc=None, attachments=None,
                reply_to=None): 

        if sender is None:
            app = _request_ctx_stack.top.app
            sender = app.config.get("DEFAULT_MAIL_SENDER")

        if isinstance(sender, tuple):
            # sender can be tuple of (name, address)
            sender = "%s <%s>" % sender

        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html

        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to

        if recipients is None:
            recipients = []

        self.recipients = list(recipients)

        if attachments is None:
            attachments = []

        self.attachments = attachments
 
    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def is_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """

        reply_to = self.reply_to or ''
        for val in [self.subject, self.sender, reply_to] + self.recipients:
            for c in '\r\n':
                if c in val:
                    return True
        return False
    
    def dump(self):
        assert self.html or self.body
        if self.html:
            msg = MIMEText(self.html,'html')
        elif self.body:
            msg = MIMEText(self.body)
        
        msg['Subject'] = self.subject
        msg['To'] = ', '.join(self.recipients) 
        msg['From'] = self.sender
        if self.cc:
            msg['CC'] = self.cc
        if self.bcc:
            msg['BCC'] = self.bcc
        if self.reply_to:
            msg['Reply-To'] = self.reply_to

        return msg.as_string()


    def send(self, mailer):
        """
        Verifies and sends the message.
        
        :param mailer: Mailer instance
        """

        assert self.recipients, "No recipients have been added"
        assert self.body or self.html, "No body or HTML has been set"
        assert self.sender, "No sender address has been set"

        if self.is_bad_headers():
            raise BadHeaderError
        
        mailer.send(self)


