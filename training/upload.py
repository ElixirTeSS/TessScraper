__author__ = 'milo'

import urllib2
import urllib
import json
import pprint

import ConfigParser
from courses import TuitionUnit


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
    def create_organization(data):
        conf = CKANUploader.get_config()
        action = '/api/3/action/organization_create'
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
        #pprint.pprint(created_package)
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
                    print "CHECKING RESULT: " + str(response_dict['result'])
                    return response_dict['result']
                else:
                    return None
            else:
                return None
        except urllib2.HTTPError as e:
            print "Check for existence failed: " + str(e)
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

    @staticmethod
    def check_data(course):
        result = CKANUploader.check_dataset(course.dump())
        if result:
            name = result['name']
            print "Got dataset: " + name
            return result
        else:
            return None

    # upload_dataset must return an id which has to be passed to upload_resource, so the resource can be linked to the dataset.
    # Therefore, the former returns None if nothing is created so that we can detect whether it has worked or not. In the case
    # of the upload_resource then the error can be returned here rather than in the rest of the script, as with upload_dataset.
    @staticmethod
    def create_or_update(course):
        data_exists = CKANUploader.check_data(course)
        if data_exists:
            changes = TuitionUnit.compare(course.dump(),data_exists)
            if changes:
                print "DATASET: Something has changed."
                # CKAN insists that for an update the _entire_ dict is uploaded again, which sucks.
                # Therefore, one must edit the existing one by applying the changes to it.
                updated = CKANUploader.update_dataset(changes)
                if updated:
                    print "Package updated."
                    # Now update the resource
                    for res in data_exists['resources']:
                        res_changes = TuitionUnit.compare(course.dump(),res)
                        if res_changes:
                            res_updated = CKANUploader.update_resource(res_changes)
                            if res_updated:
                                print "Resource updated."
            else:
                print "DATASET: No change."

        else:
            # If neither exists then they should be created.
            print "Found nothing. Creating."
            dataset = None
            try:
                dataset = CKANUploader.create_dataset(course.dump())
                return str(dataset['id'])
            except:
                print "Could not created dataset"
            if dataset:
                print "Creating resource: " + str(dataset['id'])
                #do_upload_resource(course,dataset['id'])
                try:
                    course.package_id = dataset['id']
                    course.name = course.name + "-link"
                    CKANUploader.create_resource(course.dump())
                except Exception as e:
                    print "Error whilst uploading! Details: " + str(e)
            else:
                print "Failed to create dataset so could not create resource: " + course.name
