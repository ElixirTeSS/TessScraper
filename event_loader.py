__author__ = 'milo'

import urllib2
import json
import pprint

events_url = 'http://iann.pro/solr/select/?q=*:*&rows=4&fl=start,title,country,link&fq=end%3A[NOW%20TO%20*]&wt=json'

response = urllib2.urlopen(events_url)
data = json.loads(response.read())

pprint.pprint(data)

# Save the data as a file for loading by ckan
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)


# To load this json from a file
#with open('data.json') as data_file:
#   data = json.load(data_file)
#   pprint.pprint(data)
