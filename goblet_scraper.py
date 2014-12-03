#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

# BROKEN: HTTP error 409 caused by stuff on line 118


from bs4 import BeautifulSoup
from training import *

import datetime
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
root_url = 'http://www.mygoblet.org/'
owner_org = 'goblet'

def parse_data(page):
    lessons = {}
    topic_match = re.compile('topic-tags')
    audience_match = re.compile('audience-tags')
    portal_match = re.compile('training-portal')
    #page = requests.get(root_url + page)
    #tree = html.fromstring(page.text)
    with open ("goblet.html", "r") as myfile:
        data=myfile.read().replace('\n', '')
    tree = BeautifulSoup(data)
    rows = tree.find_all('tbody')[0].find_all('tr')
    print str(len(rows))
    for row in rows:
        print "ROW: "
        links = row.find_all('a')
        for link in links:
            href = link.get('href')
            text = link.contents[0].encode('utf8','ignore')
            if topic_match.search(href):
                print "TOPIC: " + str(href)
            elif audience_match.search(href):
                print "AUDIENCE: " + str(href)
            elif portal_match.search(href):
                print "PORTAL: " + str(href)

        cells = row.find_all('td')
        print "TYPE: " + str(cells[1].get_text().strip())
        stuff = cells[0].get_text().encode('utf8','ignore').strip()
        reldate = stuff.replace(links[0].contents[0].encode('utf8','ignore'),'')
        date_modified = return_date(reldate)
        print "DATE: " + str(date_modified)


    return lessons



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




def get_metadata():
    return {
        'name' : 'goblet_materials',
        'title': 'GOBLET Training Materials',
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


#create_data(get_metadata(),create_package)
#create_data(get_data(),create_resource)
#create_multiple_entries(parse_data(),get_metadata()['name'])


# ?page=0,1,2
lessons = parse_data('training-portal')
pprint.pprint(lessons)

# store all the tutorials in here
#website = CourseWebsite()
#website.name = "GOBLET Training Materials"
#website.url = root_url + 'training-portal'

# each individual tutorial
#for key in lessons:
#    course = Tutorial()
#    course.url = key
#    course.name = lessons[key]
#    website.tuition_units.append(course)
#    pprint.pprint(course.dump())
#website.list_names()
#pprint.pprint(website.dump())

# Actually upload them. It will be essential to get the name/id of the created dataset in order that resources can be
# added to it; uploader.do_upload() should return this, but it will have to be parsed here.
#uploader = CKANUploader()
#uploader.do_upload(website)