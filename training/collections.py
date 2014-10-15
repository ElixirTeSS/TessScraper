__author__ = 'milo'

import uuid

# a class to define a website containing various elixir uk training materials
class ElixirCourseWebsite:

    def __init__(self):
        self.id = uuid.uuid4()
        self._name = None
        self._url = None
        self.elixir_uk_sector = None
        self.tuition_units = []


    def list_names(self):
        index = 0
        print "Tutorials for website " + self.name + " at " + self.url + "."
        for unit in self.tuition_units:
            print str(index) + ": " + unit.name
            index += 1

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
