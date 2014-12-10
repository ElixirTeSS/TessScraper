__author__ = 'milo'

import urllib2
import urllib
import json
import pprint

import ConfigParser


# The purpose of this file is to flip out and incorporate the code for creating new resources
# and datasets on a CKAN installation.
# http://docs.ckan.org/en/latest/user-guide.html

class CKANUploader:
    @staticmethod
    def create_dataset(data):
        conf = CKANUploader.get_config()
        action = '/api/3/action/package_create'
        url = conf['protocol'] + '://' + conf['host'] + ':' + conf['port'] + action
        return CKANUploader.__do_upload(data,url,conf)

    @staticmethod
    def create_resource(data):
        conf = CKANUploader.get_config()
        action = '/api/3/action/resource_create'
        url = conf['protocol'] + '://' + conf['host'] + ':' + conf['port'] + action
        return CKANUploader.__do_upload(data,url,conf)

    @staticmethod
    def __do_upload(data,url,conf):
        # process data to json for uploading
        print "Trying URL: " + url
        data_string = urllib.quote(json.dumps(data))
        #pprint.pprint(data_string)
        #pprint.pprint(conf)

        auth = conf['auth']
        if not auth:
            print "API string missing!"
            return

        request = urllib2.Request(url)
        request.add_header('Authorization', auth)

        # Make the HTTP request - check the apache logs to see the reason for any crashes
        #print "DATA: "
        #pprint.pprint(data)
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
        conf = CKANUploader.get_config()
        action = '/api/3/action/package_show?id='
        url = conf['protocol'] + '://' + conf['host'] + ':' + conf['port'] + action + data['name']
        print "Trying URL: " + url
        auth = conf['auth']
        if not auth:
            return
        request = urllib2.Request(url)
        request.add_header('Authorization', auth)
        try:
            response = urllib2.urlopen(request)
            if response.code == 200:
                print "GOT 200"
                response_dict = json.loads(response.read())
                if response_dict['success']:
                    return response_dict['result']
                else:
                    return None
            else:
                return None
        except urllib2.HTTPError:
            print "Check for existence failed."
            return None

    # These update methods should receive data which consist of a hash of only the
    # fields which are to be updated. I hope that that will work.
    @staticmethod
    def update_dataset(data):
        conf = CKANUploader.get_config()
        action = '/api/3/action/package_update'
        url = conf['protocol'] + '://' + conf['host'] + ':' + conf['port'] + action
        return CKANUploader.__do_upload(data,url,conf)

    @staticmethod
    def update_resource(data):
        conf = CKANUploader.get_config()
        action = '/api/3/action/resource_update'
        url = conf['protocol'] + '://' + conf['host'] + ':' + conf['port'] + action
        return CKANUploader.__do_upload(data,url,conf)

    @staticmethod
    def __do_update(data,url,conf):
        pass


    @staticmethod
    def get_config():
        error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
        Config = ConfigParser.ConfigParser()
        try:
            Config.read('uploader_config.txt')
        except error_to_catch:
            print "Can't open config file."
            return None

        host = Config.get('Main','host')
        port = Config.get('Main','port')
        protocol = Config.get('Main','protocol')
        auth = Config.get('Main','auth')

        return {'host':host,
                'port':port,
                'protocol':protocol,
                'auth':auth}
