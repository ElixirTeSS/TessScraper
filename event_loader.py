__author__ = 'milo'

import urllib2
import json
import pprint
import datetime
from dateutil import parser

def get_stuff():
    events_url = 'http://iann.pro/solr/select/?q=*:*&rows=4&fl=start,title,country,link&fq=end%3A[NOW%20TO%20*]&wt=json'

    response = urllib2.urlopen(events_url)
    data = json.loads(response.read())

    pprint.pprint(data)

    # Save the data as a file for loading by ckan
    #with open('data.json', 'w') as outfile:dt = parser.parse(entry['start'])
    #    json.dump(data, outfile)
    string = "<ul>\n"
    f = open('events.txt','w')
    for entry in data['response']['docs']:
        dt = parser.parse(entry['start'])
        string += "<li>"
        string +="<a href=\"" + entry['link'] + "\">" + entry['title'] + "</a>\n"
        string += "<br>" + dt.strftime('%A %B %d, %Y') + " &mdash; " +  entry['country']
        string += "</li>\n"
    string += "</ul>\n"
    f.write(string) # python will convert \n to os.linesep
    f.close()


def read_stuff():
    # To load this json from a file
    with open('data.json') as data_file:
        #data = json.load(data_file)
        #pprint.pprint(data)
        data = data_file.read()
        return data


get_stuff()
#result = read_stuff()
#print result
