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

root_url = 'http://software-carpentry.org/'
owner_org = 'software-carpentry'
lessons = {}


# There doesn't seem to be much need to parse this at the moment - CKAN seems to be expecting the URL of a resource
# rather than the resource itself.
def parse_data(page):
    response = urllib2.urlopen(root_url + page)
    tree = html.fromstring(response.read())
    links = tree.xpath('//ul/li/a')
    for item in links:
        href = item.attrib['href']
        title = item.text_content()
        # if href starts with v4 or v5 then it's a link to a lesson
        result = re.match('^v\d\/', href)
        if result:
            lessons[root_url + href] = title



# each individual tutorial
parse_data('lessons.html')

print "LESSONS:"
pprint.pprint(lessons)

for key in lessons:
    course = Tutorial()
    course.url = key
    course.title = lessons[key]
    course.set_name(owner_org,lessons[key])
    course.owning_org = owner_org
    course.format = 'html'
    pprint.pprint(course.dump())

    CKANUploader.create_or_update(course)


