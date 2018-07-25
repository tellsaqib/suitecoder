from utility import Utility

class ParsingHelper():

    @staticmethod
    def extractFolders(responseDOM):
        folders = []
        for folder in responseDOM.getElementsByTagName('record'):
            folderId = int(folder.getAttribute('internalId'))
            folderName = Utility.getText(folder.getElementsByTagName('name'))
            parent = 0

            parentElems = folder.getElementsByTagName('parent')
            if parentElems is not None and len(parentElems):
                parent = int(parentElems[0].getAttribute('internalId'))
            
            folders.append({'id': folderId, 'parent': parent, 'name': folderName})
        
        return folders

    @staticmethod
    def extractFiles(responseDOM, folderId):
        files = responseDOM.getElementsByTagName('record')
        fileArr = []
        for file in files:
            folder = file.getElementsByTagName('folder')[0]
            currentFolderId = folder.getAttribute('internalId')
            if currentFolderId == folderId:#making sure that this file is immediate child of currently selected folder
                fileArr.append({
                               'id': file.getAttribute('internalId'),
                               'name': Utility.getText(file.getElementsByTagName('name')),
                               'type': Utility.getText(file.getElementsByTagName('mediaTypeName')),
                               'size': Utility.getText(file.getElementsByTagName('fileSize')),
                               'date': Utility.getText(file.getElementsByTagName('lastModifiedDate'))
                               })
        return fileArr

    @staticmethod
    def extractFileContent(responseDOM):
        return Utility.getText(responseDOM.getElementsByTagName('content'))

    @staticmethod
    def getFileId(responseDOM):
        baseRef = responseDOM.getElementsByTagName('baseRef')[0]
        return baseRef.getAttribute('internalId')

    @staticmethod
    def getRoles(responseDOM):
        roleArr = []
        roles = responseDOM.getElementsByTagName('wsRole')
        for role in roles:
            roleArr.append({
                           'id': role.getElementsByTagName('role')[0].getAttribute('internalId'),
                           'name': Utility.getText(role.getElementsByTagName('name'))
                           })
        return roleArr


