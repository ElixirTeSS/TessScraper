#!/usr/bin/env python

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

from lxml import html
import requests
import re
import urllib2
import urllib
import json
import pprint


root_url = 'http://software-carpentry.org/'
page = requests.get(root_url + 'lessons.html')
tree = html.fromstring(page.text)

def get_data():
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

def get_test_data():
    return {
        'name' : 'wibble',
        'title': 'Some Exciting Example Data',
        'notes' : 'Uploaded via CKAN API'
    }

def print_data(data):
    for key in data:
        print data[key] + " : " + key

# This won't work - we'll have to create the new dataset (as in get_test_data()) and then
# add data to it somehow
def upload_data(data):
    # process data to json for uploading
    data_string = urllib.quote(json.dumps(data))
    pprint.pprint(data_string)

    # get the api key for authorisation
    with open ("api.txt", "r") as apifile:
        api = apifile.read().replace('\n', '')
    request = urllib2.Request('http://tesstest2.oerc.ox.ac.uk/api/action/package_create')
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



upload_data(get_test_data())

