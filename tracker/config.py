from os import environ

SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_URI','sqlite:///carart.db')

SECRET_KEY = 'developmentKey'
SIGNING_KEY = 'signingKey'
SIGNING_MAX_AGE = 18000 
DEVELOPMENT = True
TESTING = False
DEBUG = True

# Mail settings
MAIL_SERVER = "mail.example.com"
MAIL_PORT = 25
MAIL_USERNAME = "TEST"
MAIL_PASSWORD = "Wouldn't You Like To Know"
MAIL_FAIL_SILENTLY = False
DEFAULT_MAIL_SENDER = "test@example.com"

