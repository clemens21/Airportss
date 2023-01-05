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
import cpi

# cpi.update()

# I need airplane type (metl, mepl, heavyjet, lightjet, mediumjet)
# 6.67 pounds to 1 gallon jet fuel

# CSV paths C:\Users\12565\Desktop\projects\AirSim\python\setup
airplane_csv = "C:\\Users\\12565\\Desktop\\projects\\AirSim\\python\\setup\\allAirplanes.json"
airplane_csv_uhoh = "C:\\Users\\12565\\Desktop\\projects\\AirSim\\python\\setup\\allAirplanes_brok.json"

numberofplanes = 648 #?
pbar = tqdm(total = numberofplanes)

# Standard session info
trust_env = False
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
next_url = 'https://aerocorner.com/aircraft/boeing-747-8-freighter/'
old_url = ''
try:
    # Create initial session
    session = requests.Session()
    session.trust_env = trust_env
    session.headers = headers

    myplanes = dict()
    myplanes['airplanes'] = dict()

    while next_url:

        if old_url == next_url: break

        pbar.set_description(f"Processing {next_url.split('/')[-2]}")
        pbar.update(1)

        page = session.get(next_url)
        
        if not page.status_code == 200: starttime = time.time()
        else: html_contents = page.text

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
            page = session.get(next_url)
            html_contents = page.text
        page.close()

        soup = BeautifulSoup(html_contents, 'html.parser')
        old_url = next_url
        next_url = soup.find(id="ac_sticky_rel_next")['href']
        
        if next_url == 'https://aerocorner.com': break

        # Get standard info
        header = soup.find("dl")
        name = soup.find('h1').string
        desc = soup.find(id="primary").p.string
        try: img = soup.find("picture").contents[-2].next_element['src']
        except: img = ''
        if name in myplanes['airplanes']: pdb.set_trace()
        country = ''
        manufactured = ''
        manufacturer = ''
        icao = ''
        price = ''

        info = [x.replace('\n','') for x in header.stripped_strings]

        for i in range(len(info)-1):
            if ':' in info[i]:
                if 'country' in info[i].lower():
                    if ':' not in info[i+1]: country = info[i+1]
                elif 'manufactured' in info[i].lower():
                    if ':' not in info[i+1]: manufactured = info[i+1]
                elif 'manufacturer' in info[i].lower(): 
                    if ':' not in info[i+1]: manufacturer = info[i+1]
                elif 'icao' in info[i].lower(): 
                    if ':' not in info[i+1]: icao = info[i+1]
                elif 'price' in info[i].lower(): 
                    if ':' not in info[i+1]:
                        dolla = float(info[i+1].split()[0].split('$')[-1]) * 1000000.0
                        inflationyear = ''
                        if '(' in info[i+1]:
                            inflationyear = info[i+1].split('(')[-1][:-1]
                        if inflationyear:
                            dolla = cpi.inflate(dolla, int(inflationyear))
                        price = str(round(dolla,2))

        # if 'helicopter' in manufacturer.lower(): continue

        myplanes['airplanes'][name] = dict()
        myplanes['airplanes'][name]['name'] = name
        myplanes['airplanes'][name]['img'] = img
        myplanes['airplanes'][name]['info'] = dict()
        myplanes['airplanes'][name]['info']['country'] = country
        if desc: myplanes['airplanes'][name]['info']['description'] = desc
        else: myplanes['airplanes'][name]['info']['description'] = ''
        myplanes['airplanes'][name]['info']['manufactured'] = manufactured
        myplanes['airplanes'][name]['info']['manufacturer'] = manufacturer
        myplanes['airplanes'][name]['info']['icao'] = icao
        myplanes['airplanes'][name]['info']['price_usd'] = price
        myplanes['airplanes'][name]['info']['url'] = old_url

        # Get performance
        performance = soup.find(id="performance")
        for element in performance.next_elements:
            if isinstance(element,str): continue
            try: element['class']
            except: continue
            if element['class'][0] == 'col-sm-5':
                if 'avionics' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys: myplanes['airplanes'][name]['info']['avionics'] = ', '.join(mys)
                    else: myplanes['airplanes'][name]['info']['avionics'] = ''
                elif 'engine' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys: myplanes['airplanes'][name]['info']['engine'] = ', '.join(mys)
                    else: myplanes['airplanes'][name]['info']['engine'] = ''
                elif 'max cruise speed' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['cruise_speed_knots'] = mys[0].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['cruise_speed_knots'] = ''
                elif 'approach speed' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['approach_speed_knots'] = mys[0].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['approach_speed_knots'] = ''
                elif 'range' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['range_nm'] = mys[0].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['range_nm'] = ''
                elif 'fuel' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g'] = mys[0].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g'] = ''
                elif 'ceiling' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['ceiling_ft'] = mys[0].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['ceiling_ft'] = ''
                elif 'climb' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['climb_rate_ft_per_s'] = mys[0].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['climb_rate_ft_per_s'] = ''
                elif 'take' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['take_off_d_ft'] = mys[0].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['take_off_d_ft'] = ''
                elif 'landing' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['landing_d_ft'] = mys[0].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['landing_d_ft'] = ''
                    break

        # Get weights
        weights = soup.find(id="weights")
        for element in weights.next_elements:
            if isinstance(element,str): continue
            try: element['class']
            except: continue
            if element['class'][0] == 'col-sm-8':
                if 'take off' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['mtow_lbs'] = mys[-1].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['mtow_lbs'] = ''
                elif 'landing' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['mlw_lbs'] = mys[-1].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['mlw_lbs'] = ''
                elif 'payload' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['max_payload_lbs'] = mys[-1].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['max_payload_lbs'] = ''
                elif 'fuel' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[0]: myplanes['airplanes'][name]['info']['fuel_capacity_g'] = mys[0].strip().split()[0].replace(',','')
                    else: myplanes['airplanes'][name]['info']['fuel_capacity_g'] = ''
                elif 'baggage' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['baggage_volume_ft3'] = mys[-1].strip().split()[-2].replace(',','')
                    else: myplanes['airplanes'][name]['info']['baggage_volume_ft3'] = ''
                    break

        # Get airplane type
        myplanes['airplanes'][name]['type'] = ''
        if 'turboshaft' in myplanes['airplanes'][name]['info']['engine'].lower() or 'heli' in myplanes['airplanes'][name]['info']['manufacturer'].lower() or 'heli' in myplanes['airplanes'][name]['info']['description'].lower():
            myplanes['airplanes'][name]['type'] = 'heli'
        elif 'piston' in myplanes['airplanes'][name]['info']['engine'].lower():
            try:
                if int(myplanes['airplanes'][name]['info']['engine'][0]) > 1:
                    myplanes['airplanes'][name]['type'] = 'mepl'
                else:
                    myplanes['airplanes'][name]['type'] = 'sepl'
            except: myplanes['airplanes'][name]['type'] = 'UNK'
        elif 'turboprop' in myplanes['airplanes'][name]['info']['engine'].lower():
            try:
                if int(myplanes['airplanes'][name]['info']['engine'][0]) > 1:
                    myplanes['airplanes'][name]['type'] = 'metl'
                else:
                    myplanes['airplanes'][name]['type'] = 'setl'
            except: myplanes['airplanes'][name]['type'] = 'UNK'
        else: #jet
            if myplanes['airplanes'][name]['info']['mtow_lbs']:
                if float(myplanes['airplanes'][name]['info']['mtow_lbs']) <= 12500:
                    myplanes['airplanes'][name]['type'] = 'sjet'
                elif 12500 < float(myplanes['airplanes'][name]['info']['mtow_lbs']) <= 41000:
                    myplanes['airplanes'][name]['type'] = 'mjet'
                elif 41000 < float(myplanes['airplanes'][name]['info']['mtow_lbs']) <= 255000:
                    myplanes['airplanes'][name]['type'] = 'ljet'
                elif 255000 < float(myplanes['airplanes'][name]['info']['mtow_lbs']):
                    myplanes['airplanes'][name]['type'] = 'hjet'

        # Calc fuel_capacity_g if empty
        if not myplanes['airplanes'][name]['info']['fuel_capacity_g']:
            if myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g'] and myplanes['airplanes'][name]['info']['range_nm']:
                myplanes['airplanes'][name]['info']['fuel_capacity_g'] = str(round(1.1 * float(myplanes['airplanes'][name]['info']['range_nm']) / float(myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g']),0))
        # Calc fuel_economy_nm_per_g if empty
        if not myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g']:
            if myplanes['airplanes'][name]['info']['fuel_capacity_g'] and myplanes['airplanes'][name]['info']['range_nm']:
                myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g'] = str(round(float(myplanes['airplanes'][name]['info']['range_nm']) / float(myplanes['airplanes'][name]['info']['fuel_capacity_g']) * 1.2,2))
        # Calc fuel_capacity_lbs
        if myplanes['airplanes'][name]['info']['fuel_capacity_g']:
            myplanes['airplanes'][name]['info']['fuel_capacity_lbs'] = str(6.67 * float(myplanes['airplanes'][name]['info']['fuel_capacity_g']))
        else: myplanes['airplanes'][name]['info']['fuel_capacity_lbs'] = ''
        # Calc mlw_lbs if empty
        if not myplanes['airplanes'][name]['info']['mlw_lbs']:
            if myplanes['airplanes'][name]['info']['mtow_lbs'] and myplanes['airplanes'][name]['info']['fuel_capacity_lbs']:
                myplanes['airplanes'][name]['info']['mlw_lbs'] = str(round(float(myplanes['airplanes'][name]['info']['mtow_lbs']) - float(myplanes['airplanes'][name]['info']['fuel_capacity_lbs']),0))
        # Calc lbs/h @ cruise
        if myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g'] and myplanes['airplanes'][name]['info']['range_nm']:
            myplanes['airplanes'][name]['info']['fuel_economy_lbs_per_h'] = str(float(myplanes['airplanes'][name]['info']['fuel_economy_nm_per_g'])/6.67*(1/float(myplanes['airplanes'][name]['info']['range_nm'])))
        else:
            myplanes['airplanes'][name]['info']['fuel_economy_lbs_per_h'] = ''
        # Set whether to be used or not
        if not myplanes['airplanes'][name]['info']['fuel_capacity_lbs'] or not myplanes['airplanes'][name]['type']:
            myplanes['airplanes'][name]['use'] = '0'
        else: myplanes['airplanes'][name]['use'] = '1'

        # Get dimensions
        dimensions = soup.find(id="dimensions")
        for element in dimensions.next_elements:
            if isinstance(element,str): continue
            try: element['class']
            except: continue
            if element['class'][0] == 'col-sm-8':
                if 'economy' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['max_economy_seats'] = mys[-1].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['max_economy_seats'] = ''
                elif 'business' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['max_business_seats'] = mys[-1].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['max_business_seats'] = ''
                elif 'first' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['max_first_seats'] = mys[-1].strip().split()[0]
                    else: myplanes['airplanes'][name]['info']['max_first_seats'] = ''
                elif 'exterior' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['length_ft'] = mys[-1].strip().split()[-2].replace(',','')
                    else: myplanes['airplanes'][name]['info']['length_ft'] = ''
                elif 'tail' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['height_ft'] = mys[-1].strip().split()[-2].replace(',','')
                    else: myplanes['airplanes'][name]['info']['height_ft'] = ''
                elif 'wing span' in element.string.lower():
                    mys = [e.replace('\n','').strip() for e in element.next_sibling.next_sibling if isinstance(e,str)]
                    if mys[-1]: myplanes['airplanes'][name]['info']['wing_span_ft'] = mys[-1].strip().split()[-2].replace(',','')
                    else: myplanes['airplanes'][name]['info']['wing_span_ft'] = ''
                    break

        myplanes['airplanes'][name]['sim'] = dict()
        myplanes['airplanes'][name]['sim']['msfs20'] = 0
        myplanes['airplanes'][name]['sim']['xplane12'] = 0
        myplanes['airplanes'][name]['sim']['aerofly'] = 0
        myplanes['airplanes'][name]['sim']['FlyInside'] = 0

        
    pdb.set_trace()
    out = []
    outdict = dict()
    for key in myplanes['airplanes'].keys():
        out.append(myplanes['airplanes'][key])
    outdict['airplanes'] = out


    with open(airplane_csv, 'w') as fdump:
        json.dump(outdict,fdump,indent='    ')
    fdump.close()

except Exception as e:
    print(e)
    print(name)
    pdb.set_trace()
    with open(airplane_csv_uhoh, 'w') as fdump:
        json.dump(myplanes,fdump,indent='    ')
    fdump.close()

