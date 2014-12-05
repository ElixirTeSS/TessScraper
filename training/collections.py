__author__ = 'milo'

import uuid
import os.path

# A class to define a website containing various elixir uk training materials.
# N.B. CKAN seems to expect the URL to be the URL on the CKAN site after uploading.
class CourseWebsite:

    def __init__(self):
        self.id = uuid.uuid4()
        self.name = None
        self.title = None
        self.url = None
        self.elixir_uk_sector = None
        self.tuition_units = []
        self.owning_org = None


    def list_names(self):
        index = 0
        print "Tutorials for website " + self.name + " at " + self.url + "."
        for unit in self.tuition_units:
            print str(index) + ": " + unit.name + ": " + str(unit.id) + "/" + str(unit.parent_id)
            index += 1

    # CKAN expects some JSON to be sent when creating new objects.
    def dump(self):
        data = {'name': self.name,
                'title': self.title,
                #'url': os.path.basename(self.url),
                #'url': 'wibble',
                #'url': str(self.id).encode('ascii','ignore'),
                'url': self.url,
                'owner_org': self.owning_org,
                'extras': [{'key':'origin','value':self.url}]}
        if self.elixir_uk_sector:
            data['elixir_uk_sector'] = self.elixir_uk_sector
        return data

    @property
    def name(self):
        if self._name:
            return self._name
        else:
            return "NONE"

    @name.setter
    def name(self,value):
        self._name = value

    @property
    def url(self):
        if self._url:
            return self._url
        else:
            return "NONE"

    @url.setter
    def url(self,value):
        self._url = value
