#   10% of final grade.
#   Due Wed. 4th March 2015 - end of the day.
#   All code in Python, GAE, and webapp2.
#   Deploy on GAE.


import os
import cgi
import webapp2
import jinja2

from google.appengine.ext import ndb
from google.appengine.api import mail
from gaesessions import get_current_session

class UserDetailP(ndb.Model):
    userid = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    passwd = ndb.StringProperty(required=True) 

JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class UserDetailC(ndb.Model):
    userid = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    passwd = ndb.StringProperty(required=True) 

JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        userid = cgi.escape(session.get('userid',''), quote = True)
        passwd = cgi.escape(session.get('passwd',''), quote = True)
        message = cgi.escape(session.get('message',''), quote = True)

        template = JINJA.get_template('login.html')
        self.response.write(template.render(
            { 'the_title': 'Welcome to the Login Page'} 
        ) % (userid,passwd,message))
        pass

    def post(self):
        # Check that a login and password arrived from the FORM.
        userid = self.request.get('userid')
        passwd = self.request.get('passwd')
        session = get_current_session()
        session['userid'] = userid
        session['passwd'] = passwd
        session['message'] = ''

        if userid == '' or passwd == '':
            session['message'] = "User id and password are mandatory"
            self.redirect('/login')

        else:
            # Lookup login ID in "confirmed" datastore and Check for password match..
            idConfirmed = ndb.gql("SELECT * FROM UserDetailC WHERE userid = :1 AND passwd = :2", session['userid'] ,session['passwd'])
            result = idConfirmed.fetch()
            
            if result != []:
                self.redirect('/page1')

            else:
                session['message'] = "User id or password is invalid"
                self.redirect('/login')
                
            
        # Set the user as logged in and let them have access to /page1, /page2, and /page3.  SESSIONS.
        # What if the user has forgotten their password?  Provide a password-reset facility/form.
        pass

#confirm account, put in the confirmed store and remove from pending store
class ConfirmHandler(webapp2.RequestHandler):
    def get(self):
        userid = self.request.get('type')
        idExistP = ndb.gql("SELECT * FROM UserDetailP WHERE userid = :1", userid)
        result = idExistP.fetch()

        if result != []:
            for x in result:
                userid = x.userid
                email = x.email
                passwd = x.passwd
            
            personC = UserDetailC()
            personC.userid = userid
            personC.email = email
            personC.passwd = passwd
            personC.put()
            
            pending = ndb.gql("SELECT * FROM UserDetailP WHERE userid = :1", userid)
            entry = pending.fetch()
            for i in entry:
                i.key.delete()
            self.response.write('Confirmed you may now login')

        else:
            self.response.write('Already confirmed or not a valid link')

class LogoutHandler(webapp2.RequestHandler): #logout and clear the session
    def post(self):
       session = get_current_session()
       session.clear()
       self.redirect('/login') 

class Page1Handler(webapp2.RequestHandler):
    def get(self):
        template = JINJA.get_template('page1.html')
        self.response.write(template.render(
            { 'the_title': 'This is page 1'} 
        ))

class Page2Handler(webapp2.RequestHandler):
    def get(self):
        template = JINJA.get_template('page2.html')
        self.response.write(template.render(
            { 'the_title': 'This is page 2'} 
        ))

class Page3Handler(webapp2.RequestHandler):
    def get(self):
        template = JINJA.get_template('page3.html')
        self.response.write(template.render(
            { 'the_title': 'This is page 3'} 
        ))

class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        userid = cgi.escape(session.get('userid',''), quote = True)
        email = cgi.escape(session.get('email',''),quote = True)
        passwd = cgi.escape(session.get('passwd',''),quote = True)
        passwd2 = cgi.escape(session.get('passwd2',''),quote = True)
        message = cgi.escape(session.get('message',''), quote = True)

        template = JINJA.get_template('reg.html')
        self.response.write(template.render(
            { 'the_title': 'Welcome to the Registration Page'}) % (userid,email,passwd,passwd2,message))

    def post(self):
        length = 5
        upper = False
        lower = False
        userid = self.request.get('userid')
        email = self.request.get('email') 
        passwd = self.request.get('passwd')
        passwd2 = self.request.get('passwd2')
        session = get_current_session()
        session['userid'] = userid
        session['email'] = email
        session['passwd'] = passwd
        session['passwd2'] = passwd2
        session['message'] = ''
 
        # Check if the data items from the POST are empty.
        if userid == '' or email == '' or passwd == '' or passwd2 == '':
            session['message'] = "Fields cannot be empty"
            self.redirect('/register')
        # Check if passwd == passwd2.
        if passwd != passwd2:
            session['message'] = "Passwords do not mach"
            self.redirect('/register')

        # Is the password too simple?
        if len(passwd) < length: # check length
            session['message'] = "Password is too short must be at least 5 characters long"
            self.redirect('/register')

        for i in passwd:
            if i.isupper(): #check for at least 1 uppercase
                upper = True
            if i.islower(): #check for at least 1 lowercase
                lower = True

        if upper == False:
            session['message'] = "Password must contain at least 1 uppercase letter"
            self.redirect('/register')

        if lower == False:
            session['message'] = "Password must contain at least 1 lowercase letter"
            self.redirect('/register')


        # Does the userid already exist in the "pending" datastore or in "confirmed"?        
        idExistP = ndb.gql("SELECT * FROM UserDetailP WHERE userid = :1", session['userid'])
        idExistC = ndb.gql("SELECT * FROM UserDetailC WHERE userid = :1", session['userid'])
        result1 = idExistP.fetch()
        result2 = idExistC.fetch()

        # Add registration details to "pending" datastore.
        if(result1 == [] and result2 == [] and upper == True and lower == True and len(passwd) >= length):
            session['message'] = "Success check your email"
            person = UserDetailP()
            person.userid = userid
            person.email = email
            person.passwd = passwd
            person.put()

            # Send confirmation email.
            sender_address = "Awsome Support <leewolohan20@gmail.com>"
            user_address = "Email <" + person.email + ">"
            subject = "Confirm your registration"
            body = """
            Thank you for creating an account! Please confirm your email address by
            clicking on the link below:

            http://localhost:8080/verify?type=""" + person.userid

            mail.send_mail(sender_address, user_address, subject, body)
            self.redirect('/register')

        if(result1 != [] or result2 != []):
            session['message'] = "User ID already exists"            
            self.redirect('/register')
        

app = webapp2.WSGIApplication([
    ('/register', RegisterHandler),
    ('/verify', ConfirmHandler),
    ('/', LoginHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    #Next three URLs are only available to logged-in users.
    ('/page1', Page1Handler),
    ('/page2', Page2Handler),
    ('/page3', Page3Handler),
], debug=True)
