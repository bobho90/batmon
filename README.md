# Prerequisites

Python 3.x
AppDynamics Machine Agent Installed
AppdEvents store created in Analytics

# Creation of AppdEvents Store

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

# Installation

Extract zip and configure the extension
Move the batmon folder to the following directory: /path/to/machine-agent/monitors/
Restart the machine agent

# Configuration

Modify lookup.xml to add in the REST URLs

# Optional Files

The json folder is optional, and can be removed.  It consists of sample jsons, for testing purposes.
