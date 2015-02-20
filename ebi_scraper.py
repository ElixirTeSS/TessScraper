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

        except:
            pass



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
def do_upload_dataset(course):
    try:
        pprint.pprint(course.dump())
        dataset = CKANUploader.create_dataset(course.dump())
        return str(dataset['id'])
    except:
        return None

def do_upload_resource(course,package_id):
    try:
        course.package_id = package_id
        course.name = course.name + "-link"
        created = CKANUploader.create_resource(course.dump())
        if created:
            print "Resource created!"

    except Exception as e:
        print "Error whilst uploading! Details: " + str(e)

def do_upload_organization(org):
    try:
        org = CKANUploader.create_organization(org.dump())
        return str(org['id'])
    except Exception as e:
        print "Error creating organization: " + str(e)


#Stub - to complete find li with url of last page and return its int here 
def last_page_number():
    return 3

def setup_organization():
    organization = OrgUnit()
    organization.title = 'European Bioinformatics Institute (EBI)'
    organization.name = 'european-bioinformatics-institute-ebi'
    organization.description = 'EMBL-EBI provides freely available data from life science experiments, performs basic research in computational biology and offers an extensive user training programme, supporting researchers in academia and industry.'
    organization.image_url = 'http://www.theconsultants-e.com/Libraries/Clients/European_Bioinformatics_Institute.sflb.ashx'
    do_upload_organization(organization)

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

        data_exists = CKANUploader.check_data(course)
        if data_exists:
            new_data = TuitionUnit.compare(course.dump(),data_exists)
            name = new_data[0]
            changes = new_data[1]
            if changes:
                print "DATASET: Something has changed."
                # CKAN insists that for an update the _entire_ dict is uploaded again, which sucks.
                # Therefore, one must edit the existing one by applying the changes to it.
                update_values = course.dump()
                for key,value in changes.iteritems():
                       update_values[key] = value
                updated = CKANUploader.update_dataset(update_values)
                if updated:
                    print "Package updated (1)."
            else:
                print "DATASET: No change."
            for res in data_exists['resources']:
                # update all the things
                new_data = TuitionUnit.compare(course.dump(),res)
                name = new_data[0]
                changes = new_data[1]
                if changes:
                    print "RESOURCE: Something has changed."
                    pprint.pprint(changes)
                    # CKAN insists that for an update the _entire_ dict is uploaded again, which sucks.
                    # Therefore, one must edit the existing one by applying the changes to it.
                    update_values = course.dump()
                    for key,value in changes.iteritems():
                       update_values[key] = value

                    updated = CKANUploader.update_resource(update_values)
                    if updated:
                        print "Package updated (2)."
                else:
                    print "RESOURCE: No change."

        else:
            # If neither exists then they should be created.
            print "Found nothing. Creating."
            dataset_id = do_upload_dataset(course)
            if dataset_id:
                print "Creating resource: " + str(dataset_id)
                do_upload_resource(course,dataset_id)
            else:
                print "Failed to create dataset so could not create resource: " + course.name


#setup_organization()
# each individual tutorial
first_page = '/training/online/course-list'
scrape_page(first_page)

for page_no in range(1, last_page_number() + 1):
    page = first_page + '?page=' + str(page_no)
    print "\n\n\n\n\n" + page + "\n\n\n\n\n"
    print "Scraping page: " + str(page_no)
    scrape_page(page)

