from tempfile import TemporaryFile
from csv import DictReader
import subprocess 
from datetime import date,timedelta
from hashlib import sha256

from flaskext.script import Manager,Server,prompt_pass,prompt,prompt_bool,Shell
from tracker import app
import tracker.models as models
import tracker.forms as forms
import tracker.auth as auth
import tracker.tasks as tasks
import tracker.utils as utils
#import tracker.admin.models as models

manager = Manager(app)
manager.add_command("runserver", Server())

def _make_context():
    return dict(app=app, models=models, forms=forms, utils=utils, tasks=tasks,
            ctx=app.test_request_context(), auth=auth)

try:
    manager.add_command("shell", Shell(use_bpython=True,
                        make_context=_make_context))
except TypeError:
    manager.add_command("shell", Shell(make_context=_make_context))



def password_valid():
    return True
    #passwd = sha256(prompt_pass("Please enter admin password")).hexdigest()
    #admin = admin_models.Admin.query.filter_by(username='root').first()
    #if admin is None:
        #return True
    #if passwd == admin.password:
        #return True
    #else:
        #print "Invalid Password"
        #return False


# Fill test values
@manager.command
def testvals():
    """ Management function to create test DB. Requires root admin access. """
    if prompt_bool("Are you sure you want to loose all data?"):
        if password_valid():
            try:
                from tracker import testing
            except ImportError:
                print "Unable to load module 'testing' from tracker\
                      required to build test db"
                return 1
            testing.populate_test_db() 
            print "Test values populated"
        else:
            print 'Database operation aborted.'

# Drop DB
@manager.command
def dropdb():
    """ Management function to drob DB. Requires root admin access. """
    if prompt_bool("Are you sure you want to loose all data?"):
        if password_valid(): 
            models.db.drop_all()
            print 'Database dropped'
        else:
            print 'Database operation aborted.'

# Build DB
@manager.command
def builddb():
    """ Management function to create the required DB. """ 
    models.db.create_all()
    print 'Blank database created'
    #passwd = None
    #while passwd is None:
        #passwd = prompt_pass("Please enter primary admin password")
        #passwd_confirm = prompt_pass("Please confirm password")
        #if passwd != passwd_confirm:
            #print "Passwords do not match."
            #passwd = None
    #models.db.session.add(admin_models.Admin('root',passwd,True))
    #models.db.session.commit()

# Add newly added models
@manager.command
def addnewtables():
    """ Management function to create the required DB. """ 
    if password_valid():
        models.db.create_all()

# padding 
@manager.command
def padding():
    if password_valid():
        sponspad = models.Sponsor()
        sponspad.id = 1000
        sponspad.firstname = 'PAD'
        sponspad.lastname = 'PAD'
        models.db.session.add(sponspad)
        models.db.session.commit()
        print "Sponsors padded"
        studentpad = models.Student()
        studentpad.id = 1000
        studentpad.firstname = 'PAD'
        studentpad.lastname = 'PAD'
        models.db.session.add(studentpad)
        models.db.session.commit()
        print "Students padded"
        projectpad = models.Project()
        projectpad.id = 1000
        projectpad.title = 'PAD'
        models.db.session.add(projectpad)
        models.db.session.commit()
        print "Project padded"

# Add Admin
@manager.command
def admin():
    """ Management function to add admins. """
    if password_valid(): 
        username = None
        while username is None:
            username = prompt("Please enter new admin username")
        passwd = None
        while passwd is None:
            passwd = prompt_pass("Please enter password for user '%s'"%username)
            passwd_confirm = prompt_pass("Please confirm password")
            if passwd != passwd_confirm:
                print "Passwords do not match."
                passwd = None
        models.db.session.add(admin_models.Admin(username,passwd,True))
        models.db.session.commit()
    else:
        print "Admin creation aborted"

# Delete Admin
@manager.command
def deladmin():
    """ Management function to delete admins. """
    if password_valid(): 
        username = None
        while username is None:
            username = prompt("Please enter admin username").strip()
        user = admin_models.Admin.query.filter_by(username=username).first()
        if user:
            if prompt_bool("Are you sure you want to delete user %s"%user.name):
                models.db.session.delete(user)
                models.db.session.commit()
        else:
            print "User does not exist"

if __name__ == '__main__':
    manager.run()
