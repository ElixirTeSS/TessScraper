#!/usr/bin/env python

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

from lxml import html
from bs4 import BeautifulSoup
from training import *
import requests
import re
import urllib2
import urllib
import json
import pprint

root_url = 'https://api.coursera.org/api/catalog.v1/courses'
category_url = 'https://api.coursera.org/api/catalog.v1/categories'
session_url = 'https://api.coursera.org/api/catalog.v1/sessions'
owner_org = 'coursera'
categories = {}
audience = {
    '0':'Basic undergraduates',
    '1':'Advanced undergraduates or beginning graduates',
    '2':'Advanced graduates',
    '3':'Other'
}


# There doesn't seem to be much need to parse this at the moment - CKAN seems to be expecting the URL of a resource
# rather than the resource itself.
def parse_data(page):
    response = urllib2.urlopen(root_url + page)
    lessons = json.loads(response.read())['elements']
    return lessons

def parse_categories():
    response = urllib2.urlopen(category_url)
    data = json.loads(response.read())['elements']
    for entry in data:
        categories[entry['id']] = entry['name'].encode('ascii','ignore')

def get_session(page):
    response = urllib2.urlopen(session_url + '/' + str(page))
    sessions = json.loads(response.read())['elements']
    return sessions

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



# Categories are required in order to get some information on what tags to give the lessons.
lessons = parse_data('?fields=language,shortDescription,previewLink,targetAudience&q=search&query=bioinformatics&includes=categories,sessions')
parse_categories()

pprint.pprint(lessons)

for lesson in lessons:
    urls = []
    sessions = lesson['links']['sessions'];
    for id in sessions:
        url = get_session(id)[0]['homeLink']
        urls.append(url)
    keywords = []
    for cat in lesson['links']['categories']:
        keywords.append(categories[cat])
    course = Tutorial()
    if lesson.get('previewLink',None):
        course.url = lesson['previewLink']
    else:
        course.url = urls[0]
    course.owning_org = owner_org
    course.title = lesson['name']
    course.set_name(owner_org,lesson['shortName'])
    course.audience = lesson.get('targetAudience',None)
    course.keywords = keywords
    course.format = 'html'
    course.resources = urls
    print "LESSON: "
    pprint.pprint(course.dump())


