
#   10% of final grade.
#   Due Wed. 4th March 2015 - end of the day.
#   All code in Python, GAE, and webapp2.
#   Deploy on GAE.


import os

import webapp2
import jinja2

from google.appengine.ext import ndb

class UserDetail(ndb.Model):
    userid = ndb.StringProperty()
    email = ndb.StringProperty()
    passwd = ndb.StringProperty() 
    passwd2 = ndb.StringProperty() 

JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        # Display the LOGIN form.
        pass

    def post(self):
        # Check that a login and password arrived from the FORM.
        # Lookup login ID in "confirmed" datastore.
        # Check for password match.
        # Set the user as logged in and let them have access to /page1, /page2, and /page3.  SESSIONs.
        # What if the user has forgotten their password?  Provide a password-reset facility/form.
        pass

# We need to provide for LOGOUT.

class Page1Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write( "This is page 1.")

class Page2Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write( "This is page 2.")

class Page3Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write( "This is page 3.")

class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA.get_template('reg.html')
        self.response.write(template.render(
            { 'the_title': 'Welcome to the Registration Page' } 
        ))

    def post(self):
        userid = self.request.get('userid')
        email = self.request.get('email') 
        passwd = self.request.get('passwd')
        passwd2 = self.request.get('passwd2')

        # Check if the data items from the POST are empty.
        # Check if passwd == passwd2.
        # Does the userid already exist in the "confirmed" datastore or in "pending"?
        # Is the password too simple?
        
        # Add registration details to "pending" datastore.
        # Send confirmation email.

        # Can GAE send email?
        # Can my GAE app receive email?

        # This code needs to move to the email confirmation handler.
        person = UserDetail()
        person.userid = userid
        person.email = email
        person.passwd = passwd
        person.put()

        self.redirect('/login')
        

app = webapp2.WSGIApplication([
    ('/register', RegisterHandler),
    ('/processreg', RegisterHandler),
    ('/', LoginHandler),
    ('/login', LoginHandler),
    ('/processlogin', LoginHandler),
    # Next three URLs are only available to logged-in users.
    ('/page1', Page1Handler),
    ('/page2', Page2Handler),
    ('/page3', Page3Handler),
], debug=True)
