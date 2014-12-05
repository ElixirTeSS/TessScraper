#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

# BROKEN: HTTP error 409
# [Wed Dec 03 17:26:04 2014] [error] 2014-12-03 17:26:04,746 ERROR [ckan.controllers.api]
# Validation error: "{'__type': 'Validation Error', 'name': [u'Url must be purely lowercase alphanumeric (ascii) characters and these symbols: -_']}"


from bs4 import BeautifulSoup
from training import *

from lxml import html
import datetime
import requests
import re
import pprint
import urllib2

host = 'tess.oerc.ox.ac.uk'
protocol = 'https'
create_package = protocol + '://' + host + '/api/3/action/package_create'
create_resource = protocol + '://' + host + '/api/3/action/resource_create'
root_url = 'http://www.mygoblet.org/'
owner_org = 'goblet'
lessons = {}

def parse_data(page):
    topic_match = re.compile('topic-tags')
    audience_match = re.compile('audience-tags')
    portal_match = re.compile('training-portal')
    response = urllib2.urlopen(root_url + page)
    html = response.read()
    #pprint.pprint(html)
    #with open ("goblet.html", "r") as myfile:
    #    data=myfile.read().replace('\n', '')
    tree = BeautifulSoup(html) # or data, if reading locally
    rows = tree.find_all('tbody')[0].find_all('tr')
    for row in rows:
        key = None
        name = None
        topics = []
        audience = []
        links = row.find_all('a')
        for link in links:
            href = link.get('href')
            text = link.contents[0].encode('utf8','ignore')
            if topic_match.search(href):
                topics.append(text)
            elif audience_match.search(href):
                audience.append(text)
            elif portal_match.search(href):
                key = href
                name = text
        cells = row.find_all('td')
        stuff = cells[0].get_text().encode('utf8','ignore').strip()
        reldate = stuff.replace(links[0].contents[0].encode('utf8','ignore'),'')
        date_modified = return_date(reldate)
        lessons[key] = {'audience':audience, 'topics':topics, 'last_modified':date_modified, 'name':name}


def do_uploads(course):
    try:
        dataset = CKANUploader.create_dataset(course.dump())
        course.package_id = str(dataset['id'])
        course.name = course.name + "-link"
        CKANUploader.create_resource(course.dump())
    except Exception as e:
        print "Error whilst uploading! Details: " + str(e)


def check_data(course):
    result = CKANUploader.check_dataset(course.dump())
    if  result:
        name = result['name']
        print "Got dataset: " + name
        found = False
        for res in result['resources']:
            if res['name'] == name + '-link':
                print "Got resource: " + name + '-link'
                found = True
        if found:
            return 'both'
        else:
            print "No resources found for dataset" + name
            return 'dataset'

    else:
        print "Failed to get result for dataset " + course['name']
        return 'neither'
    # https://tess.oerc.ox.ac.uk/api/3/action/package_show?id=course['name']
    # result['success'] # true/false if found anything
    # To get a resource with resource_show then its ID is required, which we don't have at this point.
    # Unless, having got the dataset above we then query it for resources.

# This monstrosity would not be required if we had a proper feed
# with the actual date in it.
def return_date(datestring):
    parts = datestring.split()
    today = datetime.date.today()
    years = 0
    months = 0
    weeks = 0
    days = 0
    year_match = re.compile('year')
    month_match = re.compile('month')
    week_match = re.compile('week')
    day_match = re.compile('day')

    if month_match.search(parts[2]):
        months = int(parts[1])
    elif year_match.search(parts[2]):
        years = int(parts[1])
    elif week_match.search(parts[2]):
        weeks = int(parts[1])

    if month_match.search(parts[4]):
        months = int(parts[3])
    elif week_match.search(parts[4]):
        weeks = int(parts[3])
    elif day_match.search(parts[4]):
        days = int(parts[3])

    diff = days + (weeks * 7) + (months * 30) + (years * 365)
    delta = datetime.timedelta(days=diff)
    earlier = today - delta

    return earlier

##################################################
# Main body of the script below, functions above #
##################################################

#pages = ['0','1','2']
pages = ['0']
for p in pages:
    parse_data('training-portal?page=' + p)
#uploader = CKANUploader(None)

# each individual tutorial
for key in lessons:
    course = Tutorial()
    course.url = root_url + key
    course.owning_org = owner_org
    course.title = lessons[key]['name']
    course.name = re.sub('[^0-9a-z_-]+', '_',lessons[key]['name'].lower())[:99]
    course.last_modified = str(lessons[key]['last_modified'])
    course.created = str(lessons[key]['last_modified'])
    course.audience = lessons[key]['audience']
    course.keywords = lessons[key]['topics']
    course.format = 'html'

    # check to see if the dataset/resource exists
    # N.B. this checks all at once, which should work because we're only creating one resource per dataset.
    data_exists = check_data(course)
    if data_exists == 'dataset':
        print "Found dataset only."
    elif data_exists == 'both':
        print "Both dataset and resource present."
    elif data_exists == 'neither':
        print "Found nothing."
        pass
    else:
        print "WTF?"
        pass

    # Create the dataset/resource
    #do_uploads(course)


