import Cookie
from google.appengine.api import urlfetch
import logging

class NSConnector:
    def __init__(self):
        self.cookie = Cookie.SimpleCookie()
    
    def open(self, options={}):
        #logging.info(options.get('data'))
    
        if options.get('data') is None:
            method = urlfetch.GET
        else:
            method = urlfetch.POST

        response = urlfetch.fetch(
                                  url=options.get('url', 'https://webservices.netsuite.com/services/NetSuitePort_2013_2'),
                                  payload=options.get('data'),
                                  method=method,
                                  headers=self._getHeaders(self.cookie, options),
                                  allow_truncated=False,
                                  follow_redirects=False,
                                  deadline=100)

        self.cookie.load(response.headers.get('set-cookie', '')) # Load the cookies from the response
        #logging.info(response.content)
        if options.get('type', 'SOAP') == 'SOAP':
            return self._parseSOAPResponse(response.content, options)
        else:
            return response.content
        
    def _getHeaders(self, cookie, options):
        import string
        import random
        headers = {
                'Host': 'www.google.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
                #'User-Agent' : options.get('action'),
                'Cookie': self._makeCookieHeader(cookie)
                    }
                  
        if(options.get('type', 'SOAP') == 'SOAP'):
                #headers.insert("POST", endPoint)
                headers["Content-Type"] = "application/xml"
                headers["SoapAction"] = options.get('action')
                headers["Content-Length"] = len(options.get('data'))
        #else:
        #    headers["Cookie"] = self._makeCookieHeader(cookie)
        return headers

    def _makeCookieHeader(self, cookie):
        cookieHeader = ""
        for value in cookie.values():
            cookieHeader += "%s=%s; " % (value.key, value.value)
        return cookieHeader
      
    def _parseSOAPResponse(self, responseData, options):
        from xml.dom.minidom import parseString
        import re
        from utility import Utility
        
        responseData = re.sub(r'<[a-zA-Z_][a-zA-Z_0-9]*:', '<', responseData)
        responseData = re.sub(r'</[a-zA-Z_][a-zA-Z_0-9]*:', '</', responseData)
        
        #logging.info(responseData)
        dom = parseString(responseData)
        status = dom.getElementsByTagName('status')
        
        if len(status) > 0 and status[0].getAttribute('isSuccess') == 'true':
                return True,dom
        
        #logging.info(
        #              re.sub(r'<password>[a-zA-Z_][a-zA-Z_0-9]*</password>', ' ', options.get('data'))
        #              + ',' + responseData
        #              )
        return False,Utility.getText(dom.getElementsByTagName('message')[0])