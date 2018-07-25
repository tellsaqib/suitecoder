import webapp2
import json
import calendar
import sys

from google.appengine.api import users
from google.appengine.ext import ndb

from utility import Utility
from models import *

class HistoryHandler(webapp2.RequestHandler):

    def get(self):
        if self.request.get('action') == 'getList':
            self.getList(self.request.get('fileid'))
            
        elif self.request.get('action') == 'getContent':
            self.getContent(self.request.get('key'))

    def post(self):
        requestParams = json.loads(self.request.body)
        
        if self.request.get('action') == 'saveTag':
            record = ndb.Key(urlsafe = requestParams.get('key')).get()
            record.tag_text = requestParams.get('tag')
            record.put()
            
    def getList(self, fileId):
        fileHistory = History()
        historyRecs = fileHistory.getList(users.get_current_user().user_id(), fileId)
        returnObj = []
        if historyRecs.count() > 0:
            for historyRec in historyRecs:
                returnObj.append({
                'key': historyRec.key.urlsafe(),
                'time':calendar.timegm(historyRec.date_created.utctimetuple()),#.strftime("%Y-%m-%d %H:%M:%S"),
                'tag': historyRec.tag_text
                })

            self.response.out.write(json.dumps({"status":True,"records":returnObj}))
        else:
            self.response.out.write(json.dumps({"status":False, "message": "No Revision History Found."}))

    def getContent(self, revisionKey):
        record = ndb.Key(urlsafe=revisionKey).get()
        if record.user_id == users.get_current_user().user_id():
            self.response.out.write(json.dumps({'status': True, 'content': record.content}))
        else:
            self.response.out.write(json.dumps({'status':False, 'msg':'Permission Denied'}))