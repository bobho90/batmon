#For Python3

import json
import requests
import time
import xml.etree.ElementTree as ET
import collections
import sys
import logging, logging.config
import os
from urllib.parse import urlparse, parse_qsl
import configparser

if not os.path.exists("logs"):
    os.makedirs("logs")
    
def configure_logger(name):
	logging.config.fileConfig('conf/logging.ini')
	return logging.getLogger(name)

logs = configure_logger('default')

config = configparser.ConfigParser()
config.sections()
config.read('conf/config.ini')

globalAccountName = config['DEFAULT']['globalAccountName']
apiKey = config['DEFAULT']['apiKey']
controllerAccount = config['DEFAULT']['controllerAccount']
authorization = config['DEFAULT']['authorization']
applicationName = config['DEFAULT']['applicationName']
controllerURL = config['DEFAULT']['controllerURL']
eventServiceURL = config['DEFAULT']['eventServiceURL']

# Review: Any particular reason why the execution frequency is 30 seconds? We typically use 60 seconds. 
# Review: I see no logging whatsoever in this extension. This will make troubleshooting very complicated. 
# Review: You can have something like a config.yml file for users to enter the custom event request endpoint, event type, summary etc. The current architecture will force you to 
# make a coding change everytime you wish to send a new event or change any of the event parameters. With a config.yml, you can configure multiple events without having to touch the python code. 

#Read URLs
# tree = ET.parse('conf/lookup.xml')
# root = tree.getroot()
lookupURL = open('conf/lookup.json').read()

#Read Mappings
messages = ET.parse('conf/message.xml')
messagesroot = messages.getroot()

#Initialize Lists for Metrics
metrics = []
metricsseverity = []
checks = []
checkcritical = []
mappingdata = {}
severitydata = {}
tempdata = {}
appnames = []
appids = []
defaultAppID = []

#check mapping
if not os.path.isfile('conf/timer.json'):
	mappingexists = False
	fout = open('conf/timer.json', 'a')
	fout.write("")
	fout.close()
else:
	mappingexists = True
	with open('conf/timer.json') as json_data:
		readdata = json.load(json_data)

def applookup(appname):
	if (len(appnames) == 0):
		headers = { 'Authorization':'Basic '+authorization+''
			}
		r = requests.get(controllerURL+'/controller/rest/applications?output=json', headers=headers)
		if (r.status_code == 400):
			r = requests.get(controllerURL+'controller/rest/applications?output=json', headers=headers)
		# print(r.text)
		logs.info("Getting list of Applications")
		logs.debug('URL: '+controllerURL+'/controller/rest/applications?output=json')
		logs.debug("Headers: "+str(headers))

		applist = json.loads(r.text)
		i = 0
		while(i < len(applist)):
			appnames.append(applist[i]["name"].lower())
			appids.append(applist[i]["id"])
			if (applist[i]["name"].lower() == applicationName.lower()):
				defaultAppID.append(applist[i]["id"])
			i=i+1
		# print("ran once")
	if (appname.lower() in appnames):
		i = appnames.index(appname.lower())
		logs.info("Application Found")
		logs.debug("AppID: "+str(appids[i]))
		return(appids[i])
	# print(defaultAppID[0])
	logs.info("Application Not Found, defaulting to "+applicationName)
	logs.debug("AppID: "+str(defaultAppID[0]))
	return(defaultAppID[0])
	# i = 0
	# while(i < len(appnames)):
		# if (appnames[i] == appname.lower()):
			# return(appids[i])
		# elif (appnames[i] == applicationName.lower()):
			# defaultAppID = appids[i]
			# i=i+1
		# else:
			# i=i+1

###########
# CustomAPI function makes an AppDynamics API Call to create custom events.
###########
def customapi(app, tier, process, error, desc, severitylevel):
	appID = applookup(app)
	#Authentication against admin.vendor
	headers = { 'Authorization':'Basic '+authorization+''
		}
		
	#############
	# Uploads custom events into AppDynamics
	#############
	# Custom Events contains the following:
	# Custom Event Type - batmon
	# Severity - @severitylevel
	# Summary - Application: @app | Tier: @tier | Process: @process | Error Code: @error | Description: @desc
	# Properties:
	#	- severity (values: INFO, WARN, ERROR)
	#	- application
	#	- tier
	#	- process
	#	- type (values: EVENT)
	#############
	customevent = requests.post(controllerURL+'/controller/rest/applications/'+str(appID)+'/events?severity='+severitylevel+'&summary=Application: '+app+' | Tier: '+tier+' | Process: '+process+' | Error Code: '+error+' | Description: '+desc+'&eventtype=CUSTOM&customeventtype=batmon&propertynames=severity&propertynames=application&propertynames=tier&propertynames=process&propertynames=type&propertyvalues='+severitylevel+'&propertyvalues='+app+'&propertyvalues='+tier+'&propertyvalues='+process+'&propertyvalues=EVENT', headers=headers)
	if (customevent.status_code == 400):
		customevent = requests.post(controllerURL+'controller/rest/applications/'+str(appID)+'/events?severity='+severitylevel+'&summary=Application: '+app+' | Tier: '+tier+' | Process: '+process+' | Error Code: '+error+' | Description: '+desc+'&eventtype=CUSTOM&customeventtype=batmon&propertynames=severity&propertynames=application&propertynames=tier&propertynames=process&propertynames=type&propertyvalues='+severitylevel+'&propertyvalues='+app+'&propertyvalues='+tier+'&propertyvalues='+process+'&propertyvalues=EVENT', headers=headers)
	data = '[{"eventType": "Batmon", "guid": "batmon", "eventTypeKey": "Batmon Event", "Date": "", "displayName": "", "summaryMessage":"'+desc+'", "eventMessage": "'+error+'", "application_name": "'+app+'", "node_name": "'+process+'", "tier_name": "'+tier+'", "healthRuleEvent": "false", "healthRule_name": "", "incident_name": "", "healthRuleViolationEvent": "", "severity": "'+severitylevel+'", "deepLink": ""}]'
	logs.debug('Custom Events URL: '+controllerURL+'/controller/rest/applications/'+str(appID)+'/events?severity='+severitylevel+'&summary=Application: '+app+' | Tier: '+tier+' | Process: '+process+' | Error Code: '+error+' | Description: '+desc+'&eventtype=CUSTOM&customeventtype=batmon&propertynames=severity&propertynames=application&propertynames=tier&propertynames=process&propertynames=type&propertyvalues='+severitylevel+'&propertyvalues='+app+'&propertyvalues='+tier+'&propertyvalues='+process+'&propertyvalues=EVENT')
	logs.debug("Headers: "+str(headers))
	logs.info("Custom Events Posted")
###########
# CustomAPI function makes an AppDynamics API Call to inset into the appdevents table.
###########
def eventsapi(app, tier, process, error, desc, severitylevel):
	#Authentication to Events Service for appdevents table
	appd_headers = { 'Content-Type':'application/vnd.appd.events+json',
		'X-Events-API-AccountName':globalAccountName,
		'X-Events-API-Key':apiKey
		}
	#############
	# Prepares data to be sent to appdevents table, with all the values updated
	#############	
	data = '[{"eventType": "Batmon", "guid": "batmon", "eventTypeKey": "Batmon Event", "Date": "", "displayName": "", "summaryMessage":"'+desc+'", "eventMessage": "'+error+'", "application_name": "'+app+'", "node_name": "'+process+'", "tier_name": "'+tier+'", "healthRuleEvent": "false", "healthRule_name": "", "incident_name": "", "healthRuleViolationEvent": "", "severity": "'+severitylevel+'", "deepLink": ""}]'
	#print(data)
	appdevent = requests.post(eventServiceURL+'/events/publish/AppdEvents', headers=appd_headers, data=data)
	logs.debug(eventServiceURL+'/events/publish/AppdEvents')
	logs.debug("Headers: "+str(appd_headers))
	logs.debug("Data: "+str(data))
	logs.info("Posted into Analytics")
###########
# API function makes 2 AppDynamics API Calls.
# It creates a custom event and sends data into the appdevents table in AppDynamics.
###########
def api(app, tier, process, error, desc, severitylevel):
	appID = applookup(app)
	# print(str(appID))
	# print(app)
	#Authentication against admin.vendor
	headers = { 'Authorization':'Basic '+authorization+''
		}
		
	#Authentication to Events Service for appdevents table
	appd_headers = { 'Content-Type':'application/vnd.appd.events+json',
		'X-Events-API-AccountName':globalAccountName,
		'X-Events-API-Key':apiKey
		}
		
	#############
	# Uploads custom events into AppDynamics
	#############
	# Custom Events contains the following:
	# Custom Event Type - batmon
	# Severity - @severitylevel
	# Summary - Application: @app | Tier: @tier | Process: @process | Error Code: @error | Description: @desc
	# Properties:
	#	- severity (values: INFO, WARN, ERROR)
	#	- application
	#	- tier
	#	- process
	#	- type (values: EVENT)
	#############

	# Review: Please add some logging for when a request fails to go through

	customevent = requests.post(controllerURL+'/controller/rest/applications/'+str(appID)+'/events?severity='+severitylevel+'&summary=Application: '+app+' | Tier: '+tier+' | Process: '+process+' | Error Code: '+error+' | Description: '+desc+'&eventtype=CUSTOM&customeventtype=batmon&propertynames=severity&propertynames=application&propertynames=tier&propertynames=process&propertynames=type&propertyvalues='+severitylevel+'&propertyvalues='+app+'&propertyvalues='+tier+'&propertyvalues='+process+'&propertyvalues=EVENT', headers=headers)
	data = '[{"eventType": "Batmon", "guid": "batmon", "eventTypeKey": "Batmon Event", "Date": "", "displayName": "", "summaryMessage":"'+desc+'", "eventMessage": "'+error+'", "application_name": "'+app+'", "node_name": "'+process+'", "tier_name": "'+tier+'", "healthRuleEvent": "false", "healthRule_name": "", "incident_name": "", "healthRuleViolationEvent": "", "severity": "'+severitylevel+'", "deepLink": ""}]'
	logs.debug('Custom Events URL: '+controllerURL+'/controller/rest/applications/'+str(appID)+'/events?severity='+severitylevel+'&summary=Application: '+app+' | Tier: '+tier+' | Process: '+process+' | Error Code: '+error+' | Description: '+desc+'&eventtype=CUSTOM&customeventtype=batmon&propertynames=severity&propertynames=application&propertynames=tier&propertynames=process&propertynames=type&propertyvalues='+severitylevel+'&propertyvalues='+app+'&propertyvalues='+tier+'&propertyvalues='+process+'&propertyvalues=EVENT')
	logs.debug("Headers: "+str(headers))
	logs.info("Custom Events Posted")
	appdevent = requests.post(eventServiceURL+'/events/publish/AppdEvents', headers=appd_headers, data=data)
	logs.debug(eventServiceURL+'/events/publish/AppdEvents')
	logs.debug("Headers: "+str(appd_headers))
	logs.debug("Data: "+str(data))
	logs.info("Posted into Analytics")
###########
# ConnectionFailed function makes an AppDynamics API Call.
# When a specific URL is unreachable, it calls this function create a custom event stating issue.
###########
def connectionfailed(url, error):
	appID = applookup(applicationName)
	#Authentication against admin.vendor
	headers = { 'Authorization':'Basic '+authorization+''
		}
	#############
	# Uploads custom events into AppDynamics
	#############
	# Custom Events contains the following:
	# Custom Event Type - batmon
	# Severity - ERROR
	# Summary - Error: @error | URL: @url
	# Properties:
	#	- severity (values: ERROR)
	#	- type (values: URL)
	#############
	customevent = requests.post(controllerURL+'/controller/rest/applications/'+str(appID)+'/events?severity=ERROR&summary=Error: '+format(error)+' | URL: '+url+'&eventtype=CUSTOM&customeventtype=batmon&propertynames=severity&propertynames=type&propertyvalues=ERROR&propertyvalues=URL', headers=headers)
###########
# PostValues Function processes each list to Count and Process Error Codes and Severities
###########
def postValues():
	counter=collections.Counter(metrics)
	keys=list(counter.keys())
	values=list(counter.values())
	for i in range(len(keys)):
		print (keys[i].decode("utf-8")+",value="+str(values[i]))
	
	## Post Severity
	#print ("------------")
	counter=collections.Counter(metricsseverity)
	keys=list(counter.keys())
	values=list(counter.values())
	for i in range(len(keys)):
		print (keys[i].decode("utf-8")+",value="+str(values[i]))

# Review: How/where are these metrics being printed? 

###########
# Severity Function identifies the severity level of the message based on the application.
# It scans the message.xml file and identifies the applications and the messages for the application, then maps the severity.
# If there doesn't exist an Application or message, it will return an INFO severity.
###########
def severity(app, message):
	#############
	# Debugging
	#############
	#print ("application: "+app)
	#print ("message: "+message)
	##############
	
	for applications in messagesroot.iter('application'):
		if applications.get('name') == app:
			info = applications.find('severity/info')
			for contentmessage in info.findall('*'):
				if contentmessage.text == message:
					return ("INFO")
			warning = applications.find('severity/warning')
			for contentmessage in warning.findall('*'):
				if contentmessage.text == message:
					return ("WARN")
			critical = applications.find('severity/critical')
			for contentmessage in critical.findall('*'):
				if contentmessage.text == message:
					return ("ERROR")
			return("INFO")
	return("INFO")

###########
# Timer Function identifies the timeout between sending custom events
# It scans the message.xml file and identifies the timeout period for each application.
# If there doesn't exist any timeout, there will be no timeouts.
###########
def timer(app):
	for applications in messagesroot.iter('application'):
		if applications.get('name') == app:
			timeout = applications.find('timeout')
			if timeout == None:
				return (int(0))
			return(int(timeout.text))
	#return(int(99999))
	return(int(0))

###########
# CheckTimer Function creates a mapping of how many times the script ran.  If it equates to the timeout, it then sets updateapi to True.
###########	
def checktimer(app, severity, timer, mappingexists):
	updateapi = True
	time = 0
	init = False
	
	checks.append(app.encode('utf-8'))
	counter=collections.Counter(checks)
	keys=list(counter.keys())
	values=list(counter.values())
	
	for i in range(len(keys)):
		if (app == keys[i].decode("utf-8") and values[i] >= 1 ):
			####
			#print(keys[i].decode("utf-8"))
			if mappingexists == False:
				init = True
				mappingexists = True
				#print(mappingexists)
			elif keys[i].decode("utf-8") not in readdata:
				init = True
			else:
				time = int(readdata[keys[i].decode("utf-8")])
				
			if init == True or time == timer-1:
				time = 0
				mappingdata[keys[i].decode("utf-8")] = time
			else:
				updateapi = False
				time += 1
				mappingdata[keys[i].decode("utf-8")] = time
			
			if severity == "INFO":
				updateapi = False
			#print(time)
	
	json_data = json.dumps(mappingdata)
	#print (json_data)
	fout = open('conf/timer.json', 'w')
	fout.write(json_data)
	fout.close()
	
	#print(updateapi)
	
	return updateapi

####
	
def checkurl(url):
	if "itmonitoring" in url:
		return("new")
	else:
		return("default")
		
def processMetrics (app, tier, process, message, description):
	#Create Metric Path for each Error Code
	metric = "name=Custom Metrics|Batch Monitoring|"+app+"|"+tier+"|"+process+"|"+message
	logs.debug("Metric Processed: %s", metric)
	logs.info("Processed Metric from JSON.")

	#############
	# Debugging
	#############
	#print (metric)
	#############

	#Check Severity Level
	severitylevel = severity(app, message)

	#############
	# Debugging
	#############
	#print (severitylevel)
	#############

	#Create Metric Path for each Severity
	metricseverity = "name=Custom Metrics|Batch Monitoring|"+app+"|"+tier+"|"+process+"|Severity|"+severitylevel
	logs.debug("Processed Metric Severity: %s", metricseverity)
	logs.info("Processed Metric Severity from JSON.")

	#Checks the timeout for the application
	time = timer(app)
	#Identifies if custom events needs to be created
	doesapi=checktimer(metricseverity, severitylevel, time, mappingexists)

	#print(doesapi)
	if doesapi == True:
		#print("API CALL")
		#AppDynamics API Call
		customapi(app,tier,process,message,description,severitylevel)
	
	#print("events")
	eventsapi(app,tier,process,message,description,severitylevel)
	logs.info("Events Posted into Analytics.")

	#Append metric path to lists
	metrics.append(metric.encode('utf-8'))
	metricsseverity.append(metricseverity.encode('utf-8'))
	
#Making Rest Calls
# for rest in root.iter('rest'):
for rest in json.loads(lookupURL):
	for urls in rest['rest']:
		url = str(urls['url'])
		# url = str(rest.attrib['url'])
		# print(url)
		# labels = []
		#############
		# Used for local JSON
		# DEBUGGING ONLY
		#############
		# try:
		
		# except OSError as err:
			# logs.error("Error {0}".format(err))
			# logs.warning("File can't be opened.")
		#for line in json.loads(r):
		#############

		#############
		# Used for REST Call to get JSON
		#############
		try:
			r = requests.get(url)
			# r = open(url).read()
			if (checkurl(url) == "new"):
				#debug = "true";
				# if (debug == "true"):
					# appname = "Test"
					# tiername = "TierTest"
					# processname = "Process"
				# else:
				path = urlparse(url).path
				query = urlparse(url).query
				query_list = dict(parse_qsl(query))
				path_list = path.split("/")
				
				appname = path_list[3]
				tiername = query_list["tier"]
				processname = query_list["processName"]
				
				# print("App Name = "+appname+" | Tier Name = "+tiername+" | Process Name = "+processname)

				jsonresponse = json.loads(r.text)
				# print(json["statusCode"])
				# print(json["description"])
				message = jsonresponse["statusCode"]
				description = jsonresponse["description"]
				processMetrics(appname, tiername, processname, message, description)
			else:
				for line in json.loads(r.text):
				#############
					for field in line['fields']:
						labels.append(field['label'])

				for line in json.loads(r.text):
					for row in line['results']:
						for i in range(len(labels)-4):

							#############
							# Processed data returns the following:
							# row[0] - Application Name
							# row[1] - Tier Name
							# row[2] - Process Name
							# row[3] - Error Code/Message
							# row[4] - Error Description
							#############
							processMetrics(row[0], row[1], row[2], row[3], row[4])
					
		except OSError as err:
			#print("Error: "+format(err))
			# Review: Log an error when the http connection fails. 
			logs.error("Error: %s", connectionfailed(url, err))
			logs.debug("Error connecting to url.")
		except:
			logs.error("Error")

#Process metrics and Post to AppDynamics
postValues()
logs.info("Printing values to be posted into AppDynamics")
logs.info("--- Job Completed ---")