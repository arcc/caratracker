from flask import (make_response,redirect, url_for,
                    render_template,json,request,flash,session)
from itsdangerous import URLSafeSerializer

from . import app

serializer = URLSafeSerializer(app.config['SIGNING_KEY'])

def NYI(layout='layout.html'):
    return render_template('message.html', heading="Not Yet Implemented",
        message="Sorry for the inconvenience, this page is not yet complete",
        layout=layout)

