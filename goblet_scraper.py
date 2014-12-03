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

# ?page=0,1,2
lessons = parse_data('training-portal')
#pprint.pprint(lessons)

# store all the tutorials in here
website = CourseWebsite()
website.name = "GOBLET Training Materials"
website.url = root_url + 'training-portal'
website.owning_org = owner_org

# each individual tutorial
for key in lessons:
    course = Tutorial()
    course.url = key
    course.owning_org = website.owning_org
    course.name = lessons[key]['name']
    course.last_modified = str(lessons[key]['last_modified'])
    course.audience = lessons[key]['audience']
    course.keywords = lessons[key]['topics']
    website.tuition_units.append(course)
    pprint.pprint(course.dump())
website.list_names()
pprint.pprint(website.dump())

# Actually upload them. It will be essential to get the name/id of the created dataset in order that resources can be
# added to it; uploader.do_upload() should return this, but it will have to be parsed here.
#uploader = CKANUploader()
#uploader.do_upload(website)