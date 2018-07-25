import os
import webapp2
import json
import sys


from models import *
from google.appengine.api import users

from local_handler import LocalHandler
from account_handler import AccountHandler
from history_handler import HistoryHandler

class MainPage(webapp2.RequestHandler):

    def get(self):
        #template = JINJA_ENVIRONMENT.get_template('index.html')
        #self.response.write(template.render({}))
        with open(os.path.dirname(__file__) + '/index.html', 'r') as content_file:
            content = content_file.read()
        self.response.write(content)
        
class AppHome(webapp2.RequestHandler):

    def get(self):
        with open(os.path.dirname(__file__) + '/app.html', 'r') as content_file:
            content = content_file.read()
        self.response.write(content)        
     
app = webapp2.WSGIApplication([
('/', MainPage),
('/app', AppHome),
('/account', AccountHandler),
('/local', LocalHandler),
('/history', HistoryHandler)
], debug=False)