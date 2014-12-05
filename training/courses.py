__author__ = 'milo'

import uuid
import json

# A general class of which tutorials, face-to-face courses &c. are a subclass.
# All of these will need a name, id, url and so on, so it make sense to subclass
# the other types.
# 0: Name of tutorial
# 1: URL
# 2: Name of tutorial  it follows on from [UUID]
# 3: links to resources / tools used
# 4: DOI
# 5: Keywords
class TuitionUnit:
    def __init__(self):
        self.id = uuid.uuid4()
        self.name = None
        self.title = None
        self.url = None
        self.package_id = None # CKAN package ID
        self.parent_id = None # id of preceeding tutorial/class &c.
        self.resources = []
        self.doi = None
        self.created = None
        self.last_modified = None
        self.format = None
        self.keywords = []
        self.difficulty = None
        self.owning_org = None # CKAN owning organisation
        self.audience = []

    # CKAN expects some JSON to be sent when creating new objects.
    def dump(self):
        data = {#'id': str(self.id),
                'name': self.name,
                'title': self.title,
                'url': self.url,
                'parent_id': self.parent_id,
                'doi': self.doi,
                'format': self.format,
                'created': self.created,
                'last_modified': self.last_modified,
                'keywords': self.keywords,
                'difficulty': self.difficulty,
                'owner_org': self.owning_org,
                'package_id': self.package_id
                }
        return data

    # Compare the current (under examination) version of the data with that which is already on TeSS.
    # Return each field which needs updating as a hash, so this can be passed to the update functions.
    @staticmethod
    def compare(current,tess):
        dont_change = ['created',
                       'last_modified',
                       'last_update']
        newdata = {}
        for key in current:
            if key in dont_change:
              continue
            print "KEY(1): " + str(key)
            try:
                if current[key].encode('utf8') != tess[key].encode('utf8'):
                    print "KEYDIFF"
                    newdata[key] = current[key]
            except Exception as e:
              print "KEYFAIL:  " + str(e)
        print "NEWDATA: " + str(newdata)
        return newdata


# 6: Name of author
# 7: Date created
# 8: Date of last update
# 9: Difficulty rating out of 5 stars
class Tutorial(TuitionUnit):
    def __init__(self):
        TuitionUnit.__init__(self)
        self.author = None
        self.created = None
        self.last_update = None

    def dump(self):
        data = TuitionUnit.dump(self)
        data['author'] = self.author
        data['created'] = self.created
        data['last_update'] = self.last_update
        return data


# 6: Organisers
# 7: Date(s) of event
# 8: Difficulty rating out of 5 stars
class FaceToFaceCourse(TuitionUnit):
    def __init__(self):
        TuitionUnit.__init__(self)
        self.organisers = []
        self.dates = [] # start 0, end 1 ?

    def dump(self):
        data = TuitionUnit.dump(self)
        data['organisers'] = self.organisers
        data['dates'] = self.dates
        return data
