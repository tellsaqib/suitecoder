import urllib
import webapp2
import json
import logging
import sys

from google.appengine.api import users
from google.appengine.api import urlfetch

from models import *

from ns_connector import NSConnector
from parsing_helper import ParsingHelper
from soap_helper import SOAPHelper
from utility import Utility

class AccountHandler(webapp2.RequestHandler):

    def post(self):
        
        requestParams = json.loads(self.request.body)
        self.credObject = Utility.getCredentialsObject(requestParams)
            
        if self.request.get('action') == 'update_file':
            self.updateFile(requestParams.get('file_id'), requestParams.get('content'), requestParams.get('save_history'))

        elif self.request.get('action') == 'login':
            self.login()

        elif self.request.get('action') == 'getfolders':
            self.sendFolderList()

        elif self.request.get('action') == 'getfiles':
            folderId = self.request.get('folderid')
            self.sendFiles(folderId)

        elif self.request.get('action') == 'loadFile':
            fileId = self.request.get('id')
            self.loadFile(fileId)

        elif self.request.get('action') == 'addfile':
            fileName = self.request.get('filename')
            folderId = self.request.get('folderid')
            self.addFile(fileName, folderId)
            
    def login(self):
        if self.credObject.get('is_sandbox'):
          url = 'https://system.sandbox.netsuite.com/rest/roles'
        else:
          url = 'https://system.netsuite.com/rest/roles'
        
        response = urlfetch.fetch(url= url,
                                  method=urlfetch.GET,
                                  headers={
                                  'Authorization': 'NLAuth ' + urllib.urlencode({'nlauth_email': self.credObject.get('email', '')}) + ', ' + urllib.urlencode({'nlauth_signature': self.credObject.get('password', '')})
                                  },
                                  allow_truncated=False,
                                  follow_redirects=False,
                                  deadline=100)
                                  
        self.response.out.write(response.content)

    def sendFolderList(self):

        soap = SOAPHelper.getSOAP(self.credObject, 'folderSearch')
        #logging.info(soap)
        connector = NSConnector()
        status,data = connector.open({'data':soap
                                     , 'action':'search'
                                     , 'url': self.credObject.get('webservice_url')})

        if status:
            folderList = ParsingHelper.extractFolders(data)
            self.response.out.write(json.dumps({"status":True,"result": folderList}))
        else:
            self.response.out.write('{"status":false,"message":"' + data + '"}')

    def sendFiles(self, folderId):
        soap = SOAPHelper.getSOAP(self.credObject, 'fileSearch', {'folderId':folderId})

        connector = NSConnector()
        status,data = connector.open({'data':soap, 'action':'search', 'url': self.credObject.get('webservice_url')})

        if status:
            fileList = ParsingHelper.extractFiles(data, folderId)
            response = {'status':True,'files': fileList}
        else:
            response = {'status':False,'message': data}
            
        self.response.out.write(json.dumps(response))

    def loadFile(self, fileId):
        import base64
        soap = SOAPHelper.getSOAP(self.credObject, 'fileLoad', {'fileid':fileId})
        connector = NSConnector()
        status,data = connector.open({'data':soap, 'action':'get', 'url': self.credObject.get('webservice_url')})

        if status:
            fileContent = ParsingHelper.extractFileContent(data)
            self.response.out.write(json.dumps( {"status": True, "content": base64.b64decode(fileContent) }))
        else:
            self.response.out.write(json.dumps( {"status": False, "content":data}))

    def updateFile(self, fileId, content, saveHistory):
        import base64
        soap = SOAPHelper.getSOAP(self.credObject, 'fileUpdate', {'fileid':fileId, 'content':base64.b64encode(content.encode('utf-8'))})
        #logging.info(soap)
        connector = NSConnector()
        status,data = connector.open({'data':soap, 'action':'update', 'url': self.credObject.get('webservice_url')})

        if status:
            self.response.out.write(json.dumps({'status': True,'message': 'File Saved.'}))

            if saveHistory == True:
                fileHistory = History()
                fileHistory.file_id = self.credObject.get('account_id') + '_' + fileId
                fileHistory.user_id = users.get_current_user().user_id()
                fileHistory.tag_text = ''
                fileHistory.content = content
                fileHistory.put()
        else:
            self.response.out.write(json.dumps({'status': False,'message': 'Unable to save File.'}))
            

    def addFile(self, fileName, folderId):
        soap = SOAPHelper.getSOAP(self.credObject, 'fileAdd', {'filename':fileName, 'folderid':folderId})
        connector = NSConnector()
        status,data = connector.open({'data':soap, 'action':'add', 'url': self.credObject.get('webservice_url')})

        if status:
            fileId = ParsingHelper.getFileId(data)
            self.response.out.write(fileId)
        else:
            self.response.out.write('{"status":false,"message":"' + data + '"}')