#!/usr/bin/env python

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

# BROKEN: HTTP error 409 caused by stuff on line 118

from lxml import html
from training import *

import requests
import re
import urllib2
import urllib
import json
import pprint

host = 'tess.oerc.ox.ac.uk'
protocol = 'https'
create_package = protocol + '://' + host + '/api/3/action/package_create'
create_resource = protocol + '://' + host + '/api/3/action/resource_create'
root_url = 'http://software-carpentry.org/'
owner_org = 'sof'


# There doesn't seem to be much need to parse this at the moment - CKAN seems to be expecting the URL of a resource
# rather than the resource itself.
def parse_data():
    page = requests.get(root_url + 'lessons.html')
    tree = html.fromstring(page.text)
    links = tree.xpath('//ul/li/a')
    lessons = {}
    for item in links:
        href = item.attrib['href']
        title = item.text_content()
        # if href starts with v4 or v5 then it's a link to a lesson
        result = re.match('^v\d\/', href)
        if result:
            lessons[root_url + href] = title

    return lessons

lessons = parse_data()
#pprint.pprint(lessons)


# store all the tutorials in here
website = CourseWebsite()
website.name = "Software Carpentry"
website.url = root_url + 'lessons.html'

# each individual tutorial
for key in lessons:
    course = Tutorial()
    course.url = key
    course.name = lessons[key]
    website.tuition_units.append(course)
    pprint.pprint(course.dump())
#website.list_names()
#pprint.pprint(website.dump())

# Actually upload them. It will be essential to get the name/id of the created dataset in order that resources can be
# added to it; uploader.do_upload() should return this, but it will have to be parsed here.
#uploader = CKANUploader()
#uploader.do_upload(website)

def get_metadata():
    return {
        'name' : 'software_carpentry',
        'title': 'Software carpentry courses',
        'notes' : 'Uploaded via CKAN API',
        'owner_org': owner_org
    }

def get_data():
    return {
        'package_id' : get_metadata()['name'],
        'url': root_url + 'lessons.html',
        'description': 'Some lessons in how to write code &c.',
        'name': 'Lessons',
        'format': 'text/html'
    }

def get_test_metadata():
    return {
        'name' : 'ftang',
        'title': 'Some More Exciting Example Data',
        'notes' : 'Uploaded via CKAN API'
    }

def get_test_data():
    return {
        'package_id' : get_test_metadata()['name'],
        'url': protocol + '://' + host + '/dataset/' + get_test_metadata()['name'],
        'description': 'Nothing to see here, move along...',
        'name': 'Some test data',
        'format': 'text/plain'
    }


def print_data(data):
    for key in data:
        print data[key] + " : " + key

# This won't work - we'll have to create the new dataset (as in get_test_data()) and then
# add data to it somehow
def create_data(data,url):
    # process data to json for uploading
    data_string = urllib.quote(json.dumps(data))
    pprint.pprint(data_string)

    # get the api key for authorisation
    with open ("api.txt", "r") as apifile:
        api = apifile.read().replace('\n', '')
    request = urllib2.Request(url)
    request.add_header('Authorization', api)

    # Make the HTTP request - check the apache logs to see the reason for any crashes
    response = urllib2.urlopen(request, data_string) # 409
    assert response.code == 200

    # Use the json module to load CKAN's response into a dictionary.
    response_dict = json.loads(response.read())
    assert response_dict['success'] is True

    # package_create returns the created package as its result.
    created_package = response_dict['result']
    pprint.pprint(created_package)

def create_multiple_entries(data, name):
    for key in data:
        upload = {
            'package_id' : name,
            'url' : key,
            'name' : data[key],
            'description' : 'Uploaded via CKAN API.',
            'format' : 'text/html'
        }
        create_data(upload,create_resource)


create_data(get_test_metadata(),create_package)
#create_data(get_metadata(),create_package)
#create_data(get_data(),create_resource)
#create_multiple_entries(parse_data(),get_metadata()['name'])
