
from . import app

if not app.debug:
    import logging
    from logging import FileHandler, Formatter
    from os import path

    from flask.ext.mail import email_dispatched

    file_handler = FileHandler(path.join(app.instance_path,"tracker.log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(Formatter("""
        %(asctime)s %(levelname)s: %(message)s
        [in %(pathname)s:%(lineno)d]

        """))
    app.logger.addHandler(file_handler)


    def log_message(message, app):
        app.logger.debug(message.subject)

    email_dispatched.connect(log_message)

