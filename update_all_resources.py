from training import *
import urllib2
import urllib
import json
import pprint
import httplib    
import socket

conf = CKANUploader.get_config()

 #Get all packages
action = '/api/3/action/package_list'
url = 'http' + '://' + conf['host'] + ':' + conf['port'] + action
api = conf['auth']
request = urllib2.Request(url)
package_names = json.loads(urllib2.urlopen(request, '{}').read())


#Update each package
for package_name in package_names['result']:
	# get each package
	action = '/api/3/action/package_show'
	url = 'http' + '://' + conf['host'] + ':' + conf['port'] + action + '?id=' + package_name
	print url
	try:
		request = urllib2.Request(url)
		package_show = urllib2.urlopen(request).read()
		#Get just the JSON dump of the package 
		package = json.loads(package_show)['result']
		# CKAN won't actually update the record unless something has changed. We need to make 
		# a useless change in resources to actually get it to update
		for resource in package['resources']:
			description = resource['description']
			resource['description'] = description.rstrip() + ' '

		action = '/api/3/action/package_update'
		url = 'https' + '://' + conf['host'] + ':' + '443' + action
		try:
			request = urllib2.Request(url)
			request.add_header('Authorization', api)
			done = json.loads(urllib2.urlopen(request, json.dumps(package)).read())
			print 'Done for ' + url
		except Exception as e:
			print 'Cannot Update'
			print e
	except Exception as e:
		print 'Cannot Show'
		print e
	