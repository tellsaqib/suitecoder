import webapp2
import json
import calendar
import sys

from google.appengine.api import users
from google.appengine.ext import ndb

from models import *

class LocalHandler(webapp2.RequestHandler):

    def get(self):
            
        if self.request.get('action') == 'get_files':
            files = File.query(File.user == users.get_current_user().user_id(),
            File.folder == ndb.Key(urlsafe =self.request.get('folder')))
            
            fileList = []
            for file in files:
                fileList.append({'id': file.key.urlsafe(), 'name': file.name, 'date': calendar.timegm(file.data_modified.utctimetuple())})
            self.response.out.write(json.dumps({'status': True, 'files': fileList}))
            
        elif self.request.get('action') == 'add_file':
            file = File(
                name = self.request.get('name'),
                folder = ndb.Key(urlsafe=self.request.get('folder')),
                user = users.get_current_user().user_id()
                )
            file.put()
                
            self.response.out.write(json.dumps({'status': True, 'message':'File added.', 
                    'file':{'id': file.key.urlsafe(), 'name': file.name, 'date': calendar.timegm(file.data_modified.utctimetuple())}}))
            
        elif self.request.get('action') == 'rename':
            file = ndb.Key(urlsafe=self.request.get('file')).get()
            file.name = self.request.get('name')
            file.put()
            self.response.out.write(json.dumps({'status': True}))
            
        elif self.request.get('action') == 'delete':
            file = ndb.Key(urlsafe=self.request.get('file'))
            if file.get().user == users.get_current_user().user_id():
                file.delete()
                self.response.out.write(json.dumps({'status': True}))
            else:
                self.response.out.write(json.dumps({'status': False, 'message':'An error occurred while deleting the file.'}))
            
        elif self.request.get('action') == 'add_folder':
            folder = Folder(
                name = self.request.get('name'),
                user = users.get_current_user().user_id()
                )
            folder.put()
            self.response.out.write(json.dumps({'status': True, 'message':'Folder added', 
                    'folder':{'key': folder.key.urlsafe(), 'name': folder.name}}))
                    
        elif self.request.get('action') == 'rename_folder':
            folder = ndb.Key(urlsafe = self.request.get('folder')).get()
            if folder.user == users.get_current_user().user_id():
                folder.name = self.request.get('name')
                folder.put()
                self.response.out.write(json.dumps({'status': True}))
            else:
                self.response.out.write(json.dumps({'status': False, 'message':'An error occurred while renaming the folder.'}))
        
        elif self.request.get('action') == 'delete_folder':
            folder = ndb.Key(urlsafe=self.request.get('folder'))
            if folder.get().user == users.get_current_user().user_id():
                folder.delete()
                self.response.out.write(json.dumps({'status': True}))
            else:
                self.response.out.write(json.dumps({'status': False, 'message':'An error occurred while deleting the folder.'}))
            
        elif self.request.get('action') == 'get_folders':
            folderList = []
            
            folders = Folder.query(Folder.user == users.get_current_user().user_id())
            for folder in folders:
                folderList.append({'key': folder.key.urlsafe(),'name': folder.name})
                
            self.response.out.write(json.dumps({'status': True, 'folders': folderList}))
            
    def post(self):
        if self.request.get('action') == 'load_file':
            file = ndb.Key(urlsafe = self.request.get('id')).get()
            if file.user == users.get_current_user().user_id():
                self.response.out.write(json.dumps({'status': True, 'content': file.content}))
        else:#Save File
            postParams = json.loads(self.request.body)
            file = ndb.Key(urlsafe=postParams.get('file_id')).get()
            if file.user == users.get_current_user().user_id():
                file.content = postParams.get('content')
                file.put();
                self.response.out.write(json.dumps({'status': True, 'message': 'File Saved.'}))
                
                if postParams.get('save_history') == True:
                    fileHistory = History()
                    fileHistory.file_id = postParams.get('file_id')
                    fileHistory.user_id = users.get_current_user().user_id()
                    fileHistory.tag_text = ''
                    fileHistory.content = postParams.get('content')
                    fileHistory.put()
            else:
                self.response.out.write(json.dumps({'status': False, 'message': 'You are not authorized to view this file.'}))