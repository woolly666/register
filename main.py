#   10% of final grade.
#   Due Wed. 4th March 2015 - end of the day.
#   All code in Python, GAE, and webapp2.
#   Deploy on GAE.


import os
import cgi
import webapp2
import jinja2
import time

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
    changeReq = ndb.StringProperty(required=True) 

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

        if userid == '' and passwd == '':
            session['message'] = 'User ID and Password are mandatory'
            self.redirect('/login') 

        elif userid == '':
            session['message'] = 'User id is mandatory'
            self.redirect('/login')         

        elif passwd == '':
            session['message'] = 'Password is mandatory'
            self.redirect('/login') 

        else:
            # Lookup login ID in "confirmed" datastore and Check for password match..
            idConfirmed = ndb.gql("SELECT * FROM UserDetailC WHERE userid = :1 AND passwd = :2", session['userid'] ,session['passwd'])
            result = idConfirmed.fetch()
            
            if result != []: # Set the user as logged in and let them have access to /page1, /page2, and /page3.  SESSIONS.
                self.redirect('/page1')

            else:
                session['message'] = 'Not a valid user!'
                self.redirect('/login')             
   
        # What if the user has forgotten their password?  Provide a password-reset facility/form.
        pass

#confirm account, put in the confirmed store and remove from pending store
class ConfirmHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        template = JINJA.get_template('login.html')
        userid = cgi.escape(self.request.get('type'), quote = True)
        passwd = cgi.escape('', quote = True)
        message = ''
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
            personC.changeReq = "False"
            personC.put()
            passwd = ''
            
            pending = ndb.gql("SELECT * FROM UserDetailP WHERE userid = :1", userid)
            entry = pending.fetch()
            for i in entry:
                i.key.delete()
            message = 'Confirmed you may now login'
            self.response.write(template.render(
                { 'the_title': 'Welcome to the Login Page'} 
            )% (userid,passwd,message))
            

        else:
            message = 'Already confirmed or not a valid link'
            self.response.write(template.render(
                { 'the_title': 'Welcome to the Login Page'} 
            )% (userid,passwd,message))

class ResetHandler(webapp2.RequestHandler):
    def post(self):
        userid = self.request.get('userid')
        email = self.request.get('email')
        session = get_current_session()
        session['userid'] = userid
        session['email'] = email
        # Lookup login ID in "confirmed" datastore and Check for password match..
        idConfirmed = ndb.gql("SELECT * FROM UserDetailC WHERE userid = :1 AND email = :2", session['userid'] ,session['email'])
        result = idConfirmed.fetch()
            
        if result != []: # Email
            for i in result:
                personC = i
                personC.changeReq = "True"
                personC.put()

            # Send confirmation email.
            sender_address = "Awsome Support <leewolohan20@gmail.com>"
            user_address = "Email <" + session['email'] + ">"
            subject = "Reset your password"
            body = """http://a2-c00157339.appspot.com/change?type=""" + userid

            mail.send_mail(sender_address, user_address, subject, body)
            session.terminate()
            session['message'] = 'Check your email'
            self.redirect('/login')

        else:
           session['message'] = 'Not a valid user!'
           self.redirect('/reset1') 

    def get(self):
        session = get_current_session()
        message = cgi.escape(session.get('message',''), quote = True)
        template = JINJA.get_template('reset1.html')
        self.response.write(template.render(
            { 'the_title': 'Welcome to the Reset Page'} 
        )% (message))

class Reset2Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        session['userid'] = self.request.get('type')
        idExistC = ndb.gql("SELECT * FROM UserDetailC WHERE userid = :1", session['userid'])
        session['result'] = idExistC.fetch()
        message = cgi.escape(session.get('message',''), quote = True)

        template = JINJA.get_template('reset2.html')

        self.response.write(template.render(
            { 'the_title': 'Welcome to the Reset Page'} 
        )% (message))

    def post(self):
        session = get_current_session()
        length = 5
        digit = False
        upper = False
        lower = False
        passwd = self.request.get('passwd')
        passwd2 = self.request.get('confirmed')
        errorList = []
        result = session['result']

        if passwd == '':
            errorList.append("\nPassword cannot be empty")

        if passwd2 == '':
            errorList.append("\nPassword(again) cannot be empty")

        # Check if passwd == passwd2.
        if passwd != passwd2:
            errorList.append("\nPasswords do not mach")

        # Is the password too simple?
        if len(passwd) < length: # check length
            errorList.append("\nPassword is too short must be at least 5 characters long")

        for i in passwd:
            if i.isupper(): #check for at least 1 uppercase
                upper = True
            if i.islower(): #check for at least 1 lowercase
                lower = True
            if i.isdigit(): #check for at least 1 lowercase
                digit = True

        if upper == False:
            errorList.append("Password must contain at least 1 uppercase letter")

        if lower == False:
            errorList.append("Password must contain at least 1 lowercase letter")

        if digit == False:
            errorList.append("Password must contain at least 1 number")
            
        if(result != [] and passwd == passwd2 and upper == True and lower == True and len(passwd) >= length):  
           for i in result:
              personC = i
              if personC.changeReq == "True":
                  personC.userid = i.userid
                  personC.email = i.email
                  personC.passwd = passwd
                  personC.changeReq = "False"
                  personC.put()
                  session['message'] = 'Password changed'
                  self.redirect('login')
              else:
                  session['message'] = 'A change of password was not requested'
                  self.redirect('/login')
                  #session.terminate()

        else:
           session['message'] = ','.join(errorList)
           userid = session['userid']
           self.redirect('/change?type=' + userid)

class LogoutHandler(webapp2.RequestHandler): #logout and clear the session
    def post(self):
       session = get_current_session() 
       session.terminate()     
       self.redirect('/login') 

class Page1Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if 'userid' and 'passwd' in session:
            template = JINJA.get_template('page1.html')
            self.response.write(template.render(
                    { 'the_title': 'This is page 1'} 
            ))
        else:
            self.redirect('/login')

class Page2Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if 'userid' and 'passwd' in session:
            template = JINJA.get_template('page2.html')
            self.response.write(template.render(
                    { 'the_title': 'This is page 2'} 
            ))
        else:
            self.redirect('/login')

class Page3Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if 'userid' and 'passwd' in session:
            template = JINJA.get_template('page3.html')
            self.response.write(template.render(
                    { 'the_title': 'This is page 3'} 
            ))
        else:
            self.redirect('/login')

class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        message = cgi.escape(session.get('message',''), quote = True)
        template = JINJA.get_template('reg.html')
        self.response.write(template.render(
            { 'the_title': 'Welcome to the Registration Page'}) % (message))

    def post(self):
        length = 5
        digit = False
        uspace = False
        pspace = False
        espace = False
        upper = False
        lower = False
        userid = cgi.escape(self.request.get('userid'))
        email = cgi.escape(self.request.get('email'))
        passwd = cgi.escape(self.request.get('passwd'))
        passwd2 = cgi.escape(self.request.get('passwd2'))
        session = get_current_session()
        errorList = []
        session['message'] = ''
 
        # Check if the data items from the POST are empty.
        if userid == '':
            errorList.append("\nUser ID cannot be empty")

        if email == '':
            errorList.append("\nEmail cannot be empty")

        if passwd == '':
            errorList.append("\nPassword cannot be empty")

        if passwd2 == '':
            errorList.append("\nPassword(again) cannot be empty")

        # Check if passwd == passwd2.
        if passwd != passwd2:
            errorList.append("\nPasswords do not mach")

        # Is the password too simple?
        if len(passwd) < length: # check length
            errorList.append("\nPassword is too short must be at least 5 characters long")

        for i in passwd:
            if i.isupper(): #check for at least 1 uppercase
                upper = True
            if i.islower(): #check for at least 1 lowercase
                lower = True
            if i.isdigit(): #check for at least 1 digit
                digit = True
            if i == ' ': #check for at least 1 digit
                pspace = True

        for i in userid:
            if i == ' ': #check for at least 1 digit
                uspace = True

        for i in email:
            if i == ' ': #check for at least 1 digit
                espace = True

        if upper == False:
            errorList.append("Password must contain at least 1 uppercase letter")

        if lower == False:
            errorList.append("Password must contain at least 1 lowercase letter")

        if digit == False:
            errorList.append("Password must contain at least 1 number")
        
        if uspace == True:
            errorList.append("User ID cannot have a space")
        
        if pspace == True:
            errorList.append("Password cannot have a space")

        if espace == True:
            errorList.append("Email cannot have a space")


        # Does the userid already exist in the "pending" datastore or in "confirmed"?        
        idExistP = ndb.gql("SELECT * FROM UserDetailP WHERE userid = :1", userid)
        idExistC = ndb.gql("SELECT * FROM UserDetailC WHERE userid = :1", userid)
        result1 = idExistP.fetch()
        result2 = idExistC.fetch()

        # Add registration details to "pending" datastore.
        if(result1 == [] and result2 == [] and  userid != ""  and email != "" and uspace == False and espace == False and pspace == False and passwd == passwd2 and upper == True and lower == True and digit == True and len(passwd) >= length):               
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

            http://a2-c00157339.appspot.com/verify?type=""" + person.userid

            mail.send_mail(sender_address, user_address, subject, body)
            errorList.append("Success check your email")
            session.terminate()
            self.redirect('/register')

        if(result1 != [] or result2 != []):
            errorList.append("User ID already exists")

        session['message'] = ','.join(errorList)
        self.redirect('/register')
        

app = webapp2.WSGIApplication([
    ('/register', RegisterHandler),
    ('/verify', ConfirmHandler),
    ('/', LoginHandler),
    ('/login', LoginHandler),
    ('/reset1', ResetHandler),
    ('/change', Reset2Handler),
    ('/logout', LogoutHandler),
    #Next three URLs are only available to logged-in users.
    ('/page1', Page1Handler),
    ('/page2', Page2Handler),
    ('/page3', Page3Handler),
], debug=True)
