#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python

# Remove heliports and place in own .json

import json
import pdb

json_file_path = "C:\\Users\\12565\\Desktop\\airportss\\airports.json"
open_airports_path = "C:\\Users\\12565\\Desktop\\airportss\\openAirports.json"
closed_airports_path = "C:\\Users\\12565\\Desktop\\airportss\\closedAirports.json"
with open(json_file_path, 'r') as f:
    myairports = json.loads(f.read())
    closedairports = []
    removeclosed = []
    for i in range(len(myairports)):
        if myairports[i]['type'] == 'heliport' or myairports[i]['type'] == 'closed': removeclosed.append(i)
    for i in range(len(removeclosed)):
        ii = removeclosed[i]
        closedairport = myairports.pop(ii)
        closedairports.append(closedairport)
        removeclosed = [x-1 for x in removeclosed]
f.close()
with open(open_airports_path, 'w') as f:
    d = dict()
    d['airports'] = myairports
    json.dump(d,f,indent='    ')
f.close()
with open(closed_airports_path, 'w') as f:
    d = dict()
    d['airports'] = closedairports
    json.dump(d,f,indent='    ')
f.close()
