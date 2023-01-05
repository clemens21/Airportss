#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python

'''
Dis is for finding runway information for all collected open airports.  41015 airports
'''

import pdb
import pymongo
import json

# Get json into dict
airports_path = "C:\\Users\\12565\\Desktop\\projects\\AirSim\\python\\setup\\allAirplanes.json"
with open(airports_path, 'r') as f:
    myjson = json.loads(f.read())
f.close()


# Setup mongodb
myclient = pymongo.MongoClient("mongodb+srv://mclemens:soccer21@cluster0.oq6rwps.mongodb.net/test")
mydb = myclient["AirSim_MDB"]
mycoll = mydb["airplanes"]
pdb.set_trace()
mycoll.insert_many(myjson['airplanes'])
