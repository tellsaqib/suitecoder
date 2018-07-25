from google.appengine.ext import ndb
import logging

"""File History."""
class History(ndb.Model):
    file_id = ndb.StringProperty()
    user_id = ndb.StringProperty()
    content = ndb.TextProperty()
    tag_text = ndb.StringProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)

    def getList(self, userId, fileId):
        historyRecs = History.query(
        History.user_id == userId,
        History.file_id == fileId).order(- History.date_created)
        return historyRecs

"""
User Files
"""
class File(ndb.Model):
    name = ndb.StringProperty()
    content = ndb.TextProperty()
    folder = ndb.KeyProperty()
    data_modified = ndb.DateTimeProperty(auto_now = True)
    user = ndb.StringProperty()

"""
User Folders
"""
class Folder(ndb.Model):
    name = ndb.StringProperty()
    parent = ndb.KeyProperty()
    user = ndb.StringProperty()


