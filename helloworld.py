import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

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



class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw ):
        self.response.out.write(*a,**kw)
        
    def render_str(self,template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)
    
    def render(self,template, **kw):
        self.write(self.render_str(template, **kw))
    
    

class MainPage(Handler):
    def get(self):
        blogs=db.GqlQuery("select * from Blog order by created desc")
        self.render("frontpage.html",blogs=blogs)
    
 
    
class Blog(db.Model):
    subject=db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)

class newpostHandler(Handler):
    def get(self):
        self.render("newpost.html")
    
    def post(self):
        subject=self.request.get('subject')
        content=self.request.get('content')
    
        if subject and content:
            b=Blog(subject=subject,content=content)
            b.put()
            
            self.redirect('/')
        else:
            error="We need both subject and content!"
            self.render("newpost.html",subject=subject,content=content,error=error)

application = webapp2.WSGIApplication([
    ('/', MainPage),('/newpost', newpostHandler)
], debug=True)
