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
    auth = 'api.txt'

    @staticmethod
    def create_dataset(data):
        action = '/api/3/action/package_create'
        url = CKANUploader.protocol + '://' + CKANUploader.host + action
        return CKANUploader.__do_upload(data,url)

    @staticmethod
    def create_resource(data):
        action = '/api/3/action/resource_create'
        url = CKANUploader.protocol + '://' + CKANUploader.host + action
        return CKANUploader.__do_upload(data,url)

    @staticmethod
    def __do_upload(data,url):
        # process data to json for uploading
        print "Trying URL: " + url
        data_string = urllib.quote(json.dumps(data))
        #pprint.pprint(data_string)

        api = CKANUploader.get_api_key()
        if not api:
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

    @staticmethod
    def check_dataset(data):
        action = '/api/3/action/package_show?id='
        url = CKANUploader.protocol + '://' + CKANUploader.host + action + data['name']
        api = CKANUploader.get_api_key()
        if not api:
            return
        request = urllib2.Request(url)
        request.add_header('Authorization', api)
        response = urllib2.urlopen(request)
        assert response.code == 200
        response_dict = json.loads(response.read())
        if response_dict['success']:
            return response_dict['result']
        else:
            return None

    @staticmethod
    def get_api_key():
        # get the api key for authorisation
        error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
        try:
            with open (CKANUploader.auth, "r") as apifile:
                api = apifile.read().replace('\n', '')
                return api
        except error_to_catch:
            print "Can't open api file: " + CKANUploader.auth
            return None
