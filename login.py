import webapp2
import logging
import jinja2
import random
from string import letters
import hashlib
import os
import re
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)



class BlogHandler(webapp2.RequestHandler):
    """we define a subclass of the google request handler so we can add in useful methods"""
    def write(self, *a, **kw):
        """this just simplifies notation"""
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        '''params['user'] = self.user'''
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
        
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)
            
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        
    def initialize(self, *a, **kw):
        """overriding the default initialisation to always check for the user ID, needs us to add
        .by_id method to User class"""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

SECRET='jags'

class User(db.Model):
    username=db.StringProperty(required=True)
    passwordHash=db.StringProperty(required=True)
    email=db.StringProperty()
    created=db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def by_id(cls, uid):
        """given user ID returns a User object"""
        return User.get_by_id(uid, parent = users_key())
    
    @classmethod
    def by_username(cls, name):    
        u = User.all().filter('username =', name).get()
        return u
    
    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = makePasswordHash(name, pw)
        return User(parent = users_key(),
                    username = name,
                    passwordHash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_username(name)
        if u and valid_pw(name, pw, u.passwordHash):
            return u
        


def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(s):
    t=hash_str(s)
    return s+'|'+t

def check_secure_val(h):
    ###Your code here
    l=h.split('|')
    if l[1]==hash_str(l[0]):
        return l[0]
    else:
        return None



def verifyCookie(cookie_val):
    user_id=cookie_val.split('|')[0]
    return cookie_val==make_secure_val(user_id)

def makeSalt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def makePasswordHash(name,pwd,salt=None):
    if not salt:
        salt=makeSalt()
    h = hashlib.sha256(name + pwd + salt).hexdigest()
    return '%s,%s' % (salt, h)



def namefromID(userID):
    query=User.get_by_id(int(userID))
    return query.username
    
username_re=re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
pword_re=re.compile(r"^.{3,20}$")
email_re=re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def escape_html(s):
    newlist=[]
    for i in s:
        if i=='>':
            newlist.append('&gt;')
        elif i=='<':
            newlist.append('&lt;')
        elif i=='"':
            newlist.append('&quot;')
        elif i=='&':
            newlist.append('&amp;')
        else:
            newlist.append(i)
    news=''.join(newlist)
    return news



def verifyname(name):
    if username_re.match(name):
        message=''
    else:
        message="Username not valid."
    query=db.GqlQuery("select * from User where username =:name1", name1=name)
    if query.count()>0:
        message="This user name is already taken!"
    return message

def verifyusername(name):
    if username_re.match(name):
        message=True
    else:
        message=False
    query=db.GqlQuery("select * from User where username =:name1", name1=name)
    if query.count()>0:
        message=True
    return message

    
def verifypwords(password,verify):
    if pword_re.match(password):
        if password==verify:
            return ''
        else:
            return 'The passwords do not match.'
    else:
        return 'The password is not valid'


def verifyemail(email):
    if email_re.match(email) or email=='':
        return ''
    else:
        return 'The email you entered is not valid'

def matchName(userName):
    q=User.gql("where username = :1",userName)
    if q.count()>0:
        return ''
    else:
        return "Username does not exist!"
    
def matchPwd(userName,password):
    u=User.gql("where username = :1",userName).get()
    salt=u.passwordHash.split(',')[0]
    pwdHash=makePasswordHash(userName,password,salt)
    if u.passwordHash==pwdHash:
        return ''
    return "Incorrect Password"

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == makePasswordHash(name, password, salt)



class signupHandler(BlogHandler):
    def get(self):
        self.render("signup.html")
    
    def post(self):
        
        self.username=self.request.get('username')
        self.password=self.request.get('password')
        self.verify=self.request.get('verify')
        self.email=self.request.get('email')
        
        params=dict(username=self.username,email=self.email)
        have_error=False
        
        name_err=verifyname(self.username)
        pword_err=verifypwords(self.password,self.verify)
        email_err=verifyemail(self.email)
        
        if not name_err=='':
            params['name_err']=name_err
            have_error=True
        if not pword_err=='':
            params['pword_err']=pword_err
            have_error=True
        if not email_err=='':
            params['email_err']=email_err
            have_error=True
        
        if have_error:
            self.render("signup.html",**params)
        else:
            u=User.register(self.username,self.password,self.email)
            u.put()
            
            self.login(u)
            self.redirect("/blog/welcome")
    
class redirectHandler(BlogHandler):
    def get(self):
        self.redirect("/blog/login")
    
class logoutHandler(BlogHandler):
    def get(self):
        self.logout()
        self.redirect("/blog/signup")

class welcomeHandler(BlogHandler):
    def get(self):
        username = self.user.username #changed this from the homework solution
        if verifyusername(username):
            self.render("welcome.html", username=username)
        else:
            self.redirect("/blog/signup")

class loginHandler(BlogHandler):
    def get(self):
        self.render('login.html')
        
    def post(self):
        new_username=self.request.get('username')
        new_password=self.request.get('password')
        
        params={'username':new_username}
        name_err=matchName(new_username)
        if not name_err=='':
            params['name_err']=name_err
            self.render('login.html',**params)
        else:
            pword_err=matchPwd(new_username,new_password)
            if not (pword_err==''):
                params['pword_err']=pword_err
                self.render('login.html',**params)
            else:
                u=User.login(new_username, new_password)
                self.login(u) 
                self.redirect("/blog/welcome")


application = webapp2.WSGIApplication([('/',redirectHandler),('/blog/logout',logoutHandler),
    ('/blog/signup', signupHandler),('/blog/welcome', welcomeHandler),('/blog/login', loginHandler)
], debug=True)
