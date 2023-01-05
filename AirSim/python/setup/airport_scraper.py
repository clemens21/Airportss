#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python

'''
Dis is for finding runway information for all collected open airports.  41015 airports
'''

import json
import pdb
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import requests

# function to convert lat/lon to decimal from d/m/s
def convert2decimal(d,m,s):
    return d + (m/60) + (s/3600)

# CSV paths C:\Users\12565\Desktop\projects\AirSim\python\setup
open_airports_path = "C:\\Users\\12565\\Desktop\\projects\\AirSim\\python\\setup\\openAirports.json"
new_airports_path = "C:\\Users\\12565\\Desktop\\projects\\AirSim\\python\\setup\\AirportsAndRunways.json"
error_airports_path = "C:\\Users\\12565\\Desktop\\projects\\AirSim\\python\\setup\\AirportsAndRunways_emergencydump.json"

# Open initial csv.
with open(open_airports_path, 'r') as f:
    myairports = json.loads(f.read())
f.close()

# Standard session info
trust_env = False
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

# Create initial session.  Sessions are good for ~75 iterations
session = requests.Session()
session.trust_env = trust_env
session.headers = headers

# Set progres bar
pbar = tqdm(range(len(myairports['airports'])))

try:
    # Loop all airlines in json
    for i in pbar:

        # Current Airline Ident
        ident = myairports['airports'][i]['ident']

        # If already processed, skip
        if 'runways' in myairports['airports'][i]:
            pbar.set_description(f"Processing {ident}")
            continue

        # Contact url
        try:
            pbar.set_description(f"Processing {ident}")
            websiteurl = 'https://www.airnav.com/airport/'+ident
            page = session.get(websiteurl)
            html_contents = page.text
            if not page.status_code == 200: starttime = time.time()

            # If contacted, but session is stale, create new session
            while not page.status_code == 200:
                # If I am IP banned, it will stop
                if time.time()-starttime > 600:
                    pdb.set_trace()
                    time.sleep(15)
                page.close()
                session = requests.Session()
                session.trust_env = trust_env
                session.headers = headers
                page = session.get(websiteurl)
                html_contents = page.text
            page.close()
        # If catastophe, dump
        except:
            with open(error_airports_path, 'w') as fdump:
                json.dump(myairports,fdump,indent='    ')
            fdump.close()

        # Gather the html
        soup = BeautifulSoup(html_contents, 'html.parser')

        # For h3 headers
        for h3_element in soup.find_all('h3'):

            # If it is the runway header
            if 'runway' in h3_element.next_element.lower():

                # If runways does not exist in struct for ident, create.  Airports can have multiple runways
                if 'runways' not in myairports['airports'][i]: myairports['airports'][i]['runways'] = {}
                
                # Get specific runway info
                for runway_element in soup.find_all('h4'):

                    # If it is a heliport, dont use
                    if 'heli' in runway_element.next_element.lower(): continue

                    # Create struct for specific runway
                    myairports['airports'][i]['runways'][runway_element.next_element] = {}

                    # For elements in runway
                    for myrunway_element in runway_element.next_sibling.next_sibling.children:

                        # If element is a string, not correct
                        if isinstance(myrunway_element,str): continue

                        # If element has .b, not correct
                        try: myrunway_element.td.next_element.b

                        # Found a potential runway element
                        except:

                            # Current runway element string, case/switch statement
                            currstr = myrunway_element.td.next_element.split(':')[0].lower()

                            # Find dimensions (length) of runway
                            if 'dimensions' == currstr:
                                myairports['airports'][i]['runways'][runway_element.next_element]['length'] = myrunway_element.td.next_sibling.next_element.split(' ')[0]

                            # Find surface type
                            elif 'surface' == currstr:
                                ss = myrunway_element.td.next_sibling.next_element.lower()
                                if 'asphalt' in ss:
                                    if 'poor' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'poor_asphalt'
                                    elif 'fair' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'fair_asphalt'
                                    elif 'good' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'good_asphalt'
                                    elif 'excellent' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'excellent_asphalt'
                                    else: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'asphalt'
                                elif 'concrete' in ss:
                                    if 'poor' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'poor_concrete'
                                    elif 'fair' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'fair_concrete'
                                    elif 'good' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'good_concrete'
                                    elif 'excellent' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'excellent_concrete'
                                    else: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'concrete'
                                elif 'turf' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'turf'
                                elif 'gravel' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'gravel'
                                elif 'grass' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'grass'
                                elif 'dirt' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'dirt'
                                elif 'water' in ss: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = 'water'
                                else: myairports['airports'][i]['runways'][runway_element.next_element][currstr] = ss.split(' ')[0]

                            # Find lights
                            elif 'runway edge lights' in currstr:
                                ss = myrunway_element.td.next_sibling.next_element.lower()
                                if 'hi' in ss: myairports['airports'][i]['runways'][runway_element.next_element]['lights'] = 'h'
                                elif 'med' in ss: myairports['airports'][i]['runways'][runway_element.next_element]['lights'] = 'm'
                                elif 'low' in ss: myairports['airports'][i]['runways'][runway_element.next_element]['lights'] = 'l'
                                else: myairports['airports'][i]['runways'][runway_element.next_element]['lights'] = 'u'

                            # Find latitude
                            elif 'latitude' in currstr:
                                try:
                                    myrunway_element.td.next_sibling.next_element.split()
                                    mylat = myrunway_element.td.next_sibling.next_element
                                except: mylat = myrunway_element.next_element.next_element.next_element.next_element.next_element.next_element
                                degree = int(mylat.split('-')[0])
                                ms = mylat.split('-')[1].split('.')
                                minute = int(ms[0])
                                second = ms[1][:-1]
                                second = float(second[0:2]+'.'+second[2:])
                                myairports['airports'][i]['runways'][runway_element.next_element]['latitude'] = str(convert2decimal(degree,minute,second))
                                if ms[1][-1].lower() == 's':
                                    myairports['airports'][i]['runways'][runway_element.next_element]['latitude'] = '-'+myairports['airports'][i]['runways'][runway_element.next_element]['latitude']

                            # Find longitude
                            elif 'longitude' in currstr:
                                try:
                                    myrunway_element.td.next_sibling.next_element.split()
                                    mylon = myrunway_element.td.next_sibling.next_element
                                except: mylon = myrunway_element.next_element.next_element.next_element.next_element.next_element.next_element
                                degree = int(mylon.split('-')[0])
                                ms = mylon.split('-')[1].split('.')
                                minute = int(ms[0])
                                second = ms[1][:-1]
                                second = float(second[0:2]+'.'+second[2:])
                                myairports['airports'][i]['runways'][runway_element.next_element]['longitude'] = str(convert2decimal(degree,minute,second))
                                if ms[1][-1].lower() == 'w':
                                    myairports['airports'][i]['runways'][runway_element.next_element]['longitude'] = '-'+myairports['airports'][i]['runways'][runway_element.next_element]['longitude']
                            
                            # Find elevation
                            elif 'elevation' in currstr:
                                try: myelev = myrunway_element.td.next_sibling.next_element.split(' ')[0]
                                except: myelev = myrunway_element.next_element.next_element.next_element.next_element.next_element.next_element.split(' ')[0]
                                myairports['airports'][i]['runways'][runway_element.next_element]['elevation'] = myelev

                            # Find heading
                            elif 'heading' in currstr:
                                try: mys = myrunway_element.td.next_sibling.next_element.split('/')[-1].split(' ')[0]
                                except: mys = myrunway_element.next_element.next_element.next_element.next_element.next_element.next_element.split('/')[-1].split(' ')[0]
                                if len(mys) == 2: mys = mys+'0'
                                elif len(mys) == 3:
                                    try: int(mys)
                                    except: mys = mys[:-1]+'0'
                                else: 
                                    mys = mys[0:2]
                                myairports['airports'][i]['runways'][runway_element.next_element]['heading'] = mys

                            # Find instrument landing info
                            elif 'instrument' in currstr:
                                try: disrunway = myrunway_element.td.next_sibling.next_element.split('/')[0]
                                except: disrunway = myrunway_element.next_element.next_element.next_element.next_element.next_element.next_element.split('/')[0]
                                myairports['airports'][i]['runways'][runway_element.next_element]['landing'] = disrunway
                        
                        # If eventually, some information is not found for specific runway, put in default values
                        if 'length' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['length'] = '500'
                        if 'surface' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['surface'] = ''
                        if 'lights' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['lights'] = 'n'
                        if 'latitude' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['latitude'] = myairports['airports'][i]['coordinates'].split(', ')[1]
                        if 'longitude' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['longitude'] = myairports['airports'][i]['coordinates'].split(', ')[0]
                        if 'elevation' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['elevation'] = myairports['airports'][i]['elevation_ft']
                        if 'heading' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            # Special logic here to intelligently set default
                            if 'N/S' in runway_element.next_element: myairports['airports'][i]['runways'][runway_element.next_element]['heading'] = '180'
                            elif 'E/W' in runway_element.next_element: myairports['airports'][i]['runways'][runway_element.next_element]['heading'] = '270'
                            elif 'NE/SW' in runway_element.next_element: myairports['airports'][i]['runways'][runway_element.next_element]['heading'] = '225'
                            elif 'NW/SE' in runway_element.next_element: myairports['airports'][i]['runways'][runway_element.next_element]['heading'] = '135'
                            else:
                                mys = runway_element.next_element.split('/')[-1].split(' ')[0]
                                if len(mys) == 2: mys = mys+'0'
                                elif len(mys) == 3:
                                    try: int(mys)
                                    except: mys = mys[:-1]+'0'
                                else: mys = mys[0:2]
                                myairports['airports'][i]['runways'][runway_element.next_element]['heading'] = mys
                        if 'landing' not in myairports['airports'][i]['runways'][runway_element.next_element]:
                            myairports['airports'][i]['runways'][runway_element.next_element]['landing'] = ''

                        # End Except .b
                    # End for elements in runway
                # End get specific runway info
            # End if h3 is a runway
        # End for h3 headers
    # End for ident

    # When finished, write to new_airports_path json
    with open(new_airports_path, 'w') as f:
        json.dump(myairports,f,indent='    ')
    f.close()

# Catch ALL exceptions and dump emergency json file. Print error and let me debug
except Exception as e:
    print(e)
    with open(error_airports_path, 'w') as fdump:
        json.dump(myairports,fdump,indent='    ')
    fdump.close()
    pdb.set_trace()