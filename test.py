#Python 3

from urllib.parse import urlparse, parse_qsl
import os
import json

URL = "https://qa-api.amtrak.com/v1/itmonitoring/PTC-Prod/app-logs?tier=Batch&&processName=ActiveTrains"
urljson = "/Users/bho/OneDrive - Column Group/WIP/batmon-v4-beta/json/new.json"

path = urlparse(URL).path
query = urlparse(URL).query
query_list = dict(parse_qsl(query))

path_list = path.split(os.sep)

appname = path_list[3]
tiername = query_list["tier"]
processname = query_list["processName"]

#print (path)
#print(path_list)
#print("App Name =", appname)

#print(query)
#print(query_list)
#print(query_list["tier"])
#print(query_list["processName"])

#print("Start Here")
print("App Name = "+appname+" | Tier Name = "+tiername+" | Process Name = "+processname)

r = open(urljson).read()
json = json.loads(r)
print(json["statusCode"])
print(json["description"])