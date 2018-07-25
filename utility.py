import logging
import sys

class Utility():
		
    @staticmethod
    def getText(node):
        try:
            rc = []
            node = node[0]
            for node in node.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    rc.append(node.data)
        except:
            logging.info(sys.exc_info())
        return ''.join(rc)
	
    @staticmethod
    def makeBrowserFriendly(str):
        str = str.replace('<','&lt;').replace('>','&gt;')
        str += '<br/><br/>'
        return str
        
        
    @staticmethod
    def getCredentialsObject(requestParams):
        return {
            'email': requestParams.get('email'),
            'password': requestParams.get('password'),
            'account_id': requestParams.get('account_id'),
            'is_sandbox': requestParams.get('is_sandbox'),
            'role_id': requestParams.get('role_id'),
            'webservice_url': requestParams.get('webservice_url','') + '/services/NetSuitePort_2013_2'
            }
            
    @staticmethod
    def getFilePermissionHash(fileId, credObject):
        return str(fileId) 
        + credObject.get('email') 
        + credObject.get('role_id') 
        + credObject.get('account_id') 
        + credObject.get('is_sandbox')