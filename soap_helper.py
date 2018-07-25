class SOAPHelper():

    @staticmethod
    def getLoginSOAP(credObject):
        loginSOAP = '<?xml version="1.0" encoding="UTF-8"?>'
        loginSOAP += '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="urn:core_2013_2.platform.webservices.netsuite.com" xmlns:ns2="urn:messages_2013_2.platform.webservices.netsuite.com">'
        loginSOAP += '<SOAP-ENV:Header></SOAP-ENV:Header>'
        loginSOAP += '  <SOAP-ENV:Body>'
        loginSOAP += '    <ns2:login>'
        loginSOAP += '    <ns2:passport>'
        loginSOAP += str('    <ns1:email>' + credObject.get('email', '') + '</ns1:email>')
        loginSOAP += str('    <ns1:password>' + credObject.get('password', '') + '</ns1:password>')
        loginSOAP += str('    <ns1:account>' + credObject.get('account_id', '') + '</ns1:account>')
        loginSOAP += '	  </ns2:passport>'
        loginSOAP += '	</ns2:login>'
        loginSOAP += '  </SOAP-ENV:Body>'
        loginSOAP += '</SOAP-ENV:Envelope>'

        #return '<?xml version="1.0" encoding="UTF-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">    <soap:Header></soap:Header>    <soap:Body>        <login xmlns="urn:messages_1_0.platform.webservices.netsuite.com">            <passport><email xmlns="urn:core_2009_1.platform.webservices.netsuite.com">nsaqib@folio3.com</email><password xmlns="urn:core_2009_1.platform.webservices.netsuite.com">click12345</password><account xmlns="urn:core_2009_1.platform.webservices.netsuite.com">TSTDRV434427</account></passport></login></soap:Body></soap:Envelope>'
        return loginSOAP

    @staticmethod
    def getLogoutSOAP():
        return str('<?xml version="1.0" encoding="UTF-8"?>'
                   + '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
                   + 'xmlns:ns1="urn:messages_2013_2.platform.webservices.netsuite.com">'
                   + '<SOAP-ENV:Header></SOAP-ENV:Header>'
                   + '<SOAP-ENV:Body><ns1:logout/></SOAP-ENV:Body></SOAP-ENV:Envelope>')

    @staticmethod
    def getSOAP(credObject, action, attr={}):

        soapXML = '<?xml version="1.0" encoding="UTF-8"?>'
        soapXML += '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"'
        soapXML += ' xmlns:ns1="urn:common_2013_2.platform.webservices.netsuite.com"'
        soapXML += ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        soapXML += ' xmlns:ns2="urn:messages_2013_2.platform.webservices.netsuite.com"'
        soapXML += ' xmlns:ns3="urn:core_2013_2.platform.webservices.netsuite.com"'
        soapXML += ' xmlns:ns4="urn:filecabinet_2013_2.documents.webservices.netsuite.com"'
        soapXML += ' xmlns:ns5="urn:customization_2013_2.setup.webservices.netsuite.com">'

        soapXML += '    <SOAP-ENV:Header>'
        soapXML += '        <ns3:passport SOAP-ENV:actor="http://schemas.xmlsoap.org/soap/actor/next">'
        soapXML += str('            <email>' + credObject.get('email') + '</email>')
        soapXML += str('            <password>' + credObject.get('password') + '</password>')
        soapXML += str('            <account>' + credObject.get('account_id') + '</account>')
        soapXML += str('            <role internalId="' + str(credObject.get('role_id')) + '" xsi:type="RecordRef"/>')
        soapXML += '        </ns3:passport>'
        soapXML += '    </SOAP-ENV:Header>'
        soapXML += '    <SOAP-ENV:Body>'

        if action == 'folderSearch':
            soapXML += '<ns2:search><ns2:searchRecord xsi:type="ns1:FolderSearchBasic"/></ns2:search>'

        if action == 'fileSearch':
            soapXML += str('<ns2:search><ns2:searchRecord xsi:type="ns1:FileSearchBasic"><ns1:folder operator="anyOf"><ns3:searchValue internalId="' + attr.get('folderId') + '" type="folder"/></ns1:folder></ns2:searchRecord></ns2:search>')

        if action == 'fileLoad':
            soapXML += '<ns1:get><ns1:baseRef internalId="' + attr.get('fileid') + '" type="file" xsi:type="ns3:RecordRef"/></ns1:get>'

        if action == 'fileAdd':
            import base64
            soapXML += '<ns3:add><ns3:record xsi:type="ns4:File"><ns4:name>' + attr.get('filename') + '</ns4:name><ns4:folder internalId="' + attr.get('folderid') + '" type="folder"/><ns4:content>' + base64.b64encode('') + '</ns4:content></ns3:record></ns3:add>'

        if action == 'fileUpdate':
            soapXML += '<ns3:update><ns3:record internalId="' + attr.get('fileid') + '" xsi:type="ns4:File"><ns4:content>' + attr.get('content') + '</ns4:content></ns3:record></ns3:update>'

        if action == 'createCustomRecord':
            soapXML += '<ns2:add><ns2:record xsi:type="ns5:CustomRecordType"><ns5:recordName>SuiteCoder File SVN</ns5:recordName><ns5:scriptId>_suitecoder_file_svn</ns5:scriptId></ns2:record></ns2:add>'
            
        soapXML += '    </SOAP-ENV:Body>'
        soapXML += '</SOAP-ENV:Envelope>'

        return soapXML
