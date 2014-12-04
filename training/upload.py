__author__ = 'milo'

import urllib2
import urllib
import json
import pprint

# The purpose of this file is to flip out and incorporate the code for creating new resources
# and datasets on a CKAN installation.
# http://docs.ckan.org/en/latest/user-guide.html

# 1. Create a new Uploader, passing in the api key
# 2. Run the create_resource or create_dataset action, passing in data
class CKANUploader:
    host = 'tess.oerc.ox.ac.uk'
    protocol = 'https'

    def __init__(self, auth):
        if auth:
            self.auth = auth
        else:
            self.auth = "api.txt"

    def create_dataset(self,data):
        action = '/api/3/action/package_create'
        url = CKANUploader.protocol + '://' + CKANUploader.host + action
        return self.__do_upload(data,url)

    def create_resource(self,data):
        action = '/api/3/action/resource_create'
        url = CKANUploader.protocol + '://' + CKANUploader.host + action
        return self.__do_upload(data,url)

    def __do_upload(self,data,url):
        # process data to json for uploading
        data_string = urllib.quote(json.dumps(data))
        pprint.pprint(data_string)

        # get the api key for authorisation
        error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
        try:
            with open (self.auth, "r") as apifile:
                api = apifile.read().replace('\n', '')
        except error_to_catch:
            print "Can't open api file: " + self.auth
            return

        request = urllib2.Request(url)
        request.add_header('Authorization', api)

        # Make the HTTP request - check the apache logs to see the reason for any crashes
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        # package_create returns the created package as its result.
        created_package = response_dict['result']
        pprint.pprint(created_package)
        return created_package

