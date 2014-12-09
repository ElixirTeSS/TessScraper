__author__ = 'milo'

import uuid
import json
import re

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
	self.notes = None
	self.tags = None
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
		'notes': self.notes,
		'tags': self.tags,
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

    # The name has to be unique, not a special CKAN name (e.g. search), and no more than 100
    # characters in length, as well as containing only 0-9,a-z,- and _
    def set_name(self,owner_org,name):
        self.name = (owner_org + '-' + re.sub('[^0-9a-z_-]+', '_',name.lower()))[:99]

    # Compare the current (under examination) version of the data with that which is already on TeSS.
    # Return each field which needs updating as a hash, so this can be passed to the update functions.
    @staticmethod
    def compare(current,tess):
        return['',{}]
        dont_change = ['created',
                       'last_modified',
                       'last_update']
        newdata = {}
        for key in current:
            # This may need re-thinking - the data may be modified on TeSS, or on the originating site.
            # How should be choose which to keep?
            if key in dont_change:
                continue
            # It's likely that scraping a website won't give me all the information we need, and TeSS may
            # have some edits. If so, these should not be overwritten by the null values from the original.
            if key == None or key == 'None':
                continue
            print "KEY(1): " + str(key)
            tesskey = tess.get(key,None)
            currentkey = current[key]
            if tesskey and currentkey:
                print "C,T: " + str(currentkey.encode('utf8','ignore')) + ", " + str(tesskey.encode('utf8','ignore'))
                if currentkey.encode('utf8','ignore') != tesskey.encode('utf8','ignore'):
                    print "KEYDIFF"
                    newdata[key] = current[key]
        print "NEWDATA: " + str(newdata)
        return [tess['id'].encode('ascii'),newdata]


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
