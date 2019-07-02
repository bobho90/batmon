# Prerequisites

- Python 3.x
- AppDynamics Machine Agent Installed
- AppdEvents store created in Analytics

# File Structure

 	.
    ├── conf                    
    │   ├── config.ini				# Configuration with AppDynamics endpoints and authorizations
    │   ├── logging.ini				# Logging Configuration
    │   ├── lookup.json				# List of URLs of REST Endpoints
    │   └── message.xml				# Mapping of message and severities
	├── json
    │   └── sample.json				# Sample JSON of expected REST Call
    ├── logs
	│	└── batmon.log				# Generated logs (location can be changed in the logging.ini)
    ├── README.md					# Readme file
    ├── batmon.py					# Python script to for Batmon
    └── monitor.xml					# AppDynamics configuration file of extension
    

# Creation of AppdEvents Store

Run the following to create the AppdEvents Store in AppDynamics.

```
curl -X POST \
<REPLACE_WITH_CONTROLLERURL>/events/schema/AppdEvents \
-H 'X-Events-API-AccountName: <REPLACE_WITH_ACCOUNTNAME>' \
-H 'X-Events-API-Key: <REPLACE_WITH_APIKEY>' \
-H 'Content-Type: application/vnd.appd.events+json;v=2' \
-H 'Accept: application/vnd.appd.events+json;v=2' \
-d '{ 
   "schema" : {
		"eventType": "string",
		"guid": "string",
		"eventTypeKey": "string",
		"Date": "string",
		"displayName": "string",
		"summaryMessage": "string",
		"eventMessage": "string",
		"application_name": "string",
		"node_name": "string",
		"tier_name": "string",
		"healthRuleEvent": "string",
		"healthRule_name": "string",
		"incident_name": "string",
		"healthRuleViolationEvent": "string",
		"severity": "string",
		"deepLink": "string",
   }
}'
```
# Installation

Extract zip and configure the extension
Move the batmon folder to the following directory: /path/to/machine-agent/monitors/
Restart the machine agent

# Configuration

Modify the files below:

## ./conf/config.ini

Provide the details below:

```
- globalAccountName = <REPLACE_WITH_GLOBAL_ACCOUNT_NAME>
- apiKey = <REPLACE_WITH_GLOBAL_APIKEY>
- controllerAccount = <REPLACE_WITH_CONTROLLER_ACCOUNT_NAME>
- authorization = <REPLACE_WITH_AUTHORIZATION_IN_BASE64>
- applicationName = <REPLACE_WITH_DEFAULT_APPLICATION_NAME>
- controllerURL = <REPLACE_WITH_CONTROLLER_URL>
- eventServiceURL = <REPLACE_WITH_EVENTS_SERVICE_URL>
```

Note: to generate the authorization in base64, you can use the link below:
https://www.base64encode.org/

Example: user@account:password --> base64: dXNlckBhY2NvdW50OnBhc3N3b3Jk

## ./conf/lookup.json

Provide the details below for the REST entrypoints:

```
[
 {
   "rest": [
    {
     "url": "https://<HOSTNAME>/<VERSION>/itmonitoring/{appName}/app-logs?tier={tierName}&&processName={processName}"
	},
	{
     "url": "https://<HOSTNAME>/<VERSION>/itmonitoring/{appName}/app-logs?tier={tierName}&&processName={processName}"
	}]
 }
]
```

Note: in the REST entrypoint, they should provide the link in the following format:
https://<HOSTNAME>/<VERSION>/itmonitoring/{appName}/app-logs?tier={tierName}&&processName={processName}

- appName - Application Name
- tierName - Tier Name
- processName - Process Name

## ./conf/message.xml

Provide the details below for mapping of message severities:

```
<applications>
	<application name="{appName}">
           <timeout>{timeout}</timeout>
		<severity>
			<info>
				<message></message>
			</info>
			<warning>
				<message></message>
			</warning>
			<critical>
				<message></message>
			</critical>
		</severity>
	</application>
</applications>
```

# Optional Files

The json folder is optional, and can be removed.  It consists of sample jsons, for testing purposes.
