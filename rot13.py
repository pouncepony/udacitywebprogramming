import webapp2

form='''<!DOCTYPE html>

<html>
<head>
    <title>Unit 2 Rot 13</title>
</head>

<body>
<h1>
    Enter some text to ROT13:
</h1>
<form method='post'>
    <textarea name="text" style="height:120px;width:420px;">%(text)s</textarea>
    <br>
    <input type="submit">
</form>

</body>
</html>
'''
def writeform(text=''):
    return form %{"text":text}

alpha="abcdefghijklmnopqrstuvwxyz"
ALPHA="ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def rot(string,n=13):
    newstr=[]
    for i in range(len(string)):
        if string[i] in alpha:
            c=alpha.find(string[i])
            newstr.append(alpha[(c+n)% 26])
        elif string[i] in ALPHA:
            c=ALPHA.find(string[i])
            newstr.append(ALPHA[(c+n)% 26])
        else:
            newstr.append(string[i])
    return ''.join(newstr)

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
    

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(writeform())
    
    def post(self):
        newtext=rot(self.request.get('text'))
        escnewtext=escape_html(newtext)
        self.response.out.write(writeform(escnewtext))
    


class TestHandler(webapp2.RequestHandler):
    def get(self):
        q=self.request.get('q')
        self.response.out.write(q)
        self.response.headers['Content-Type']='text/plain'
        self.response.out.write(self.request)#

application = webapp2.WSGIApplication([
    ('/', MainPage),('.testform',TestHandler)
], debug=True)
