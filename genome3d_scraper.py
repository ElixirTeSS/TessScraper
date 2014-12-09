#!/usr/bin/env python

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

# BROKEN: HTTP error 409 caused by stuff on line 118

from lxml import html
from bs4 import BeautifulSoup
from training import *

import requests
import re
import urllib2
import urllib
import json
import pprint

root_url = 'http://genome3d.eu/'
owner_org = 'genome3d'
lessons = {}


# There doesn't seem to be much need to parse this at the moment - CKAN seems to be expecting the URL of a resource
# rather than the resource itself.
def parse_data(page):
    #response = urllib2.urlopen(root_url + page)
    #tree = BeautifulSoup(response.read())

    with open ("genome3d.html", "r") as myfile:
        data=myfile.read().replace('\n', '')
    tree = BeautifulSoup(data)

    links = tree.find("div", {"id": "context-menu"}).find_all('ul')[0].find_all('li')
    for link in links:
        item =  link.find('a')
        href = item['href']
        text= item.get_text()
        if text == 'Tutorials Home':
            continue
        lessons[href] = text.replace('Tutorial: ','')

# upload_dataset must return an id which has to be passed to upload_resource, so the resource can be linked to the dataset.
# Therefore, the former returns None if nothing is created so that we can detect whether it has worked or not. In the case
# of the upload_resource then the error can be returned here rather than in the rest of the script, as with upload_dataset.
def do_upload_dataset(course):
    try:
        dataset = CKANUploader.create_dataset(course.dump())
        return str(dataset['id'])
    except:
        return None

def do_upload_resource(course,package_id):
    try:
        course.package_id = package_id
        course.name = course.name + "-link"
        CKANUploader.create_resource(course.dump())
    except Exception as e:
        print "Error whilst uploading! Details: " + str(e)

def check_data(course):
    result = CKANUploader.check_dataset(course.dump())
    if result:
        name = result['name']
        print "Got dataset: " + name
        return result
    else:
        return None



# each individual tutorial
parse_data('tutorials/page/Public/Page/Tutorial/Index')
print "LESSONS:"
pprint.pprint(lessons)
for key in lessons:
    course = Tutorial()
    course.url = root_url + key
    course.title = lessons[key]
    course.set_name(owner_org,lessons[key])
    course.owning_org = owner_org
    course.format = 'html'
    print "COURSE: "
    pprint.pprint(course.dump())

    # Upload at present with no checking.
    dataset_id = do_upload_dataset(course)
    print "ID: " + str(dataset_id)
    if dataset_id:
        do_upload_resource(course,dataset_id)
    else:
        print "Failed to create dataset so could not create resource: " + course.name

    existing = check_data(course)
    print "EXISTING:"
    pprint.pprint(existing)
    check = TuitionUnit.compare(course.dump(),existing)
    print "CHECK:"
    pprint.pprint(check)





