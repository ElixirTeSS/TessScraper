__author__ = 'milo'

import uuid
import json
import re
import ast

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
        self.tags = []
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
                'name': self.name.decode('utf-8') if self.name else None,
                'title': self.title.decode('utf-8') if self.title else None,
                'url': self.url.decode('utf-8') if self.url else None,
                'notes': self.notes.encode('utf-8') if self.notes else None,
                #'tags': self.tags, #[x.decode('utf-8') if x else None for x in self.tags],
                #'tags': self.tags.update({(x,y.decode('utf-8')) for x,y in self.tags.items()}),
                'tags': self.tags,
                'package_id': self.package_id.decode('utf-8') if self.package_id else None,
                'parent_id': self.parent_id.decode('utf-8') if self.parent_id else None,
                'resources': [x.decode('utf-8') if x else None for x in self.resources],
                'doi': self.doi.decode('utf-8') if self.doi else None,
                'format': self.format.decode('utf-8') if self.format else None,
                'created': self.created.decode('utf-8') if self.created else None,
                'last_modified': self.last_modified.decode('utf-8') if self.last_modified else None,
                'keywords': [x.decode('utf-8') if x else None for x in self.keywords],
                'difficulty': self.difficulty.decode('utf-8') if self.difficulty else None,
                'owner_org': self.owning_org.decode('utf-8') if self.owning_org else None,
                'package_id': self.package_id.decode('utf-8') if self.package_id else None
                }
        if self.tags:
            data['tags'] = self.tags
        return data

    # The name has to be unique, not a special CKAN name (e.g. search), and no more than 100
    # characters in length, as well as containing only 0-9,a-z,- and _
    def set_name(self,owner_org,item_name):
        self.name = (owner_org + '-' + re.sub('[^0-9a-z_-]+', '_',item_name.lower()))[:99]

    # Compare the current (under examination) version of the data with that which is already on TeSS.
    # Return each field which needs updating as a hash, so this can be passed to the update functions.
    @staticmethod
    def compare(current,tess):
        dont_change = ['id',
                       'name',
                       'created',
                       'last_modified',
                       'last_update',
                       'package_id',
                       'tags', # This should be added back in when the
                       'owner_org']
        newdata = tess
        changed = False
        for key in current:
            # This may need re-thinking - the data may be modified on TeSS, or on the originating site.
            # How should be choose which to keep?
            # The answer is apparently to discard local changes.
            if key in dont_change:
                print "DON'T CHANGE: " + key
                continue
            # It's likely that scraping a website won't give me all the information we need, and TeSS may
            # have some edits. If so, these should not be overwritten by the null values from the original.
            # Overwriting with non-null entries should not be a problem, though (see above).
            if key == None or key == 'None':
                print "KEY: NONE"
                continue
            tesskey = unicode(tess.get(key,None))
            currentkey = unicode(current[key])
            if tesskey and currentkey:
                # Format can be created in lower case but comes back from the server in upper case...
                if key == 'format':
                    if currentkey.lower() != tesskey.lower():
                    #if str(currentkey).encode('utf-8','ignore').lower() != str(tesskey).encode('utf-8','ignore').lower():
                        #print "C,T: " + str(currentkey.encode('utf8','ignore')) + ", " + str(tesskey.encode('ascii'))
                        changed = True
                        newdata[key] = current[key]
                else:
                    # The literal_eval here is because what comes back from CKAN is not a list but a string which
                    # looks like a list. Therefore, to compare it with a list one must convert it into one.
                    if isinstance(currentkey,list):
                        newlist = []
                        for value in ast.literal_eval(str(tesskey)):
                            newlist.append(value)
                        if currentkey != newlist:
                            changed = True
                            newdata[key] = current[key]
                    else:
                        # I can't work out how to get around these PITA encoding issues...
                        try:
                            #print "C,T: " + currentkey + ", " + tesskey
                            if currentkey != tesskey:
                                changed = True
                                newdata[key] = current[key]
                        except UnicodeEncodeError, e:
                            print "More unicode nuisances: " + str(e)
        #print "NEWDATA: " + str(newdata)
        #return [tess['name'].encode('ascii'),tess['id'].encode('ascii'),newdata]
        if changed:
            return newdata
        else:
            return None


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
