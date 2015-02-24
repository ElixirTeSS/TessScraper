#!/usr/bin/env python

# Sources for this example script:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.ckan.org/en/latest/api/index.html#example-importing-datasets-with-the-ckan-api

# BROKEN: HTTP error 409 caused by stuff on line 118
# The breakage is caused by attemting to upload an existing record; this requires that a check be performed
# first. Unfortuantely, the check is broken.

from lxml import html
from bs4 import BeautifulSoup
from training import *
import requests
import re
import urllib2
import urllib
import json
import pprint

root_url = 'http://www.ebi.ac.uk'
owner_org = 'european-bioinformatics-institute-ebi'
lessons = {}


# There doesn't seem to be much need to parse this at the moment - CKAN seems to be expecting the URL of a resource
# rather than the resource itself.
def parse_data(page):
    response = urllib2.urlopen(root_url + page)
    tree = BeautifulSoup(response.read())
    links = tree.find("div", {"class": "item-list"}).find_all('ul')[0].find_all('li')
    count = 1
    for link in links:
        item = link.find("div", {"class": "views-field-title"}).find('a')
        description = link.find("div", {"class": "views-field-field-course-desc-value"}).get_text()
        count += 1
        try:
            topics = link.find("div", {"class": "views-field-tid"}).get_text()

            href = item['href']
            lessons[href] = {}
            text= item.get_text()
            lessons[href]['text'] = text
            lessons[href]['description'] = description
            lessons[href]['topics'] = extract_keywords(topics)

        except Exception, e:
            print "Failed to parse link: " + str(e)



# example:
# text = "\n\n      Topic: \n\n       Ontologies\n\n System\n\n"
def extract_keywords(text):
    # Remove 'Topic:', newlines, and white space.
    # Split into array of topics and reject any empty ones
    # Format for CKAN Uploader
    text = text.replace('Topic:', '')
    text = re.sub('\n', '', text)
    text = re.sub(' +',' ', text)
    keywords = text.split(' ')
    tags = []
    for keyword in keywords:
        if keyword == '' or len(keyword) < 3:
            keywords.remove(keyword)
        else:
            tags.append({"name": re.sub(r'\W+', '', keyword)})
    return tags

# upload_dataset must return an id which has to be passed to upload_resource, so the resource can be linked to the dataset.
# Therefore, the former returns None if nothing is created so that we can detect whether it has worked or not. In the case
# of the upload_resource then the error can be returned here rather than in the rest of the script, as with upload_dataset.
#Stub - to complete find li with url of last page and return its int here
def last_page_number():
    return 2

def setup_organisation():
    organisation = OrgUnit()
    organisation.title = 'European Bioinformatics Institute (EBI)'
    organisation.name = 'european-bioinformatics-institute-ebi'
    organisation.description = 'EMBL-EBI provides freely available data from life science experiments, performs basic research in computational biology and offers an extensive user training programme, supporting researchers in academia and industry.'
    organisation.image_url = 'http://www.theconsultants-e.com/Libraries/Clients/European_Bioinformatics_Institute.sflb.ashx'
    OrgUnit.upload_organisation(organisation)

def scrape_page(page):
    parse_data(page)
    for key in lessons:
        course = Tutorial()
        course.url = root_url + key
        course.notes = lessons[key]['description']
        course.title = lessons[key]['text']
        course.set_name(owner_org,lessons[key]['text'])
        course.tags = lessons[key]['topics']
        course.owning_org = owner_org
        course.format = 'html'

        # Before attempting to create anything we need to check if the resource/dataset already exists, updating it
        # as and where necessary.
        CKANUploader.create_or_update(course)


#setup_organisation()
# each individual tutorial
first_page = '/training/online/course-list'
scrape_page(first_page)

for page_no in range(1, last_page_number() + 1):
    page = first_page + '?page=' + str(page_no)
    print "\n\n\n\n\n" + page + "\n\n\n\n\n"
    print "Scraping page: " + str(page_no)
    scrape_page(page)

