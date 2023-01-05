#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python

'''
Query Airport data.  No need for classes because you are not editing airports
'''

from mongodb_manager import MongoDB_Client
from geopy import distance
from typing import TypeVar
import pdb
from geographiclib.geodesic import Geodesic

Airport = TypeVar('Airport')

class Airport:
    __airport_collection = ''
    def __init__(self,ident_='',id_='',name_='') -> Airport:
        if not ident_ and not id_ and not name_: pass
        Airport.__airport_collection = MongoDB_Client.db["airports"]
        if ident_:
            for data in self.__airport_collection.find({'ident': ident_}): data=data
        elif id_:
            for data in self.__airport_collection.find({'_id': id_}): data=data
        elif name_:
            for data in self.__airport_collection.find({'name': name_}): data=data
        else: pass
        
        self.city = data['municipality']
        self.country = data['iso_country']
        self.continent = data['continent']
        self.elevation = data['elevation_ft']
        self.id = data['_id']
        self.ident = data['ident']
        self.lat = data['coordinates'].split(', ')[-1]
        self.lon = data['coordinates'].split(', ')[0]
        self.name = data['name']
        if 'runways' in data: self.runways = data['runways']
        else: self.runways = False
        self.size = data['type']

    def __getcity__(self) -> str:
        return self.city

    def __getcountry__(self) -> str:
        return self.country

    def __getcontinent__(self) -> str:
        return self.continent

    def __getelevation__(self) -> str:
        return self.elevation

    def __getid__(self) -> str:
        return self.id

    def __getident__(self) -> str:
        return self.ident

    def __getlat__(self) -> str:
        return self.lat

    def __getlon__(self) -> str:
        return self.lon

    def __getname__(self) -> str:
        return self.name

    def __getrunways__(self) -> dict:
        return self.runways

    def __getsize__(self) -> str:
        return self.size

    def _how_many_runways(self) -> int:
        if not self.runways: return 0
        else: return self.runways.__len__()

    def _max_landing_length(self) -> tuple:
        if not self.runways: return 500,None
        l = -99999.0
        k = ''
        v = ''
        for key,value in self.runways.items():
            if float(value['length']) > l:
                l = float(value['length'])
                k = key
                v = value
        return l,k,v

    def _max_runway_surface(self) -> tuple:
        if not self.runways: return 'dirt',None,None
        sval = 10
        k = []
        v = []
        s = ''
        surfaces1 = ['excellent_asphalt','excellent_concrete']
        surfaces2 = ['good_asphalt','good_concrete']
        surfaces3 = ['asphalt','concrete']
        surfaces4 = ['fair_asphalt','fair_concrete']
        surfaces5 = ['poor_asphalt','poor_concrete']
        surfaces6 = ['gravel','turf','grass','dirt']
        
        for key,value in self.runways.items():
            currsval = 10
            if value['surface'] in surfaces1: currsval = 1
            elif value['surface'] in surfaces2: currsval = 2
            elif value['surface'] in surfaces3: currsval = 3
            elif value['surface'] in surfaces4: currsval = 4
            elif value['surface'] in surfaces5: currsval = 5
            elif value['surface'] in surfaces6: currsval = 6
            
            if currsval < sval:
                sval = currsval
                k = []
                v = []
                s = value['surface']
                v.append(value)
                k.append(key)
            elif currsval == sval:
                v.append(value)
                k.append(key)
        
        return s,k,v

    def _can_land_at_night(self) -> tuple:
        if not self.runways: return False
        q = False
        k = []
        v = []
        for key,value in self.runways.items():
            if value['lights'] in ('h','m','l','u'):
                q = True
                k.append(key)
                v.append(value)
        return q,k,v

    def _get_size_int(self) -> int:
        if self.size == 'medium_airport': return 2
        elif self.size == 'large_airport': return 3
        else: return 1

    def _get_continent_str(self) -> str:
        if self.continent == 'NA': return 'North America'
        elif self.continent == 'AS': return 'Asia'
        elif self.continent == 'EU': return 'Europe'
        elif self.continent == 'AF': return 'Africa'
        elif self.continent == 'OC': return 'Oceania'
        elif self.continent == 'SA': return 'South America'
        elif self.continent == 'AN': return 'Antartica'
        else: return ''

    def _get_country_str(self) -> str:
        fullcountry = ['Afghanistan','\u00c5land Islands','Albania','Algeria','American Samoa',
                        'Andorra','Angola','Anguilla','Antarctica','Antigua and Barbuda',
                        'Argentina','Armenia','Aruba','Australia','Austria','Azerbaijan','Bahamas',
                        'Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bermuda',
                        'Bhutan','Bolivia (Plurinational State of)','Bonaire','Bosnia and Herzegovina',
                        'Botswana','Bouvet Island','Brazil','British Indian Ocean Territory','Brunei Darussalam',
                        'Bulgaria','Burkina Faso','Burundi','Cabo Verde','Cambodia','Cameroon','Canada','Cayman Islands',
                        'Central African Republic','Chad','Chile','China','Christmas Island','Cocos (Keeling) Islands',
                        'Colombia','Comoros','Congo','Congo','Cook Islands','Costa Rica','C\u00f4te d''Ivoire',
                        'Croatia','Cuba','Cura\u00e7ao','Cyprus','Czechia','Denmark','Djibouti','Dominica',
                        'Dominican Republic','Ecuador','Egypt','El Salvador','Equatorial Guinea','Eritrea','Estonia',
                        'Eswatini','Ethiopia','Falkland Islands (Malvinas)','Faroe Islands','Fiji','Finland','France',
                        'French Guiana','French Polynesia','French Southern Territories','Gabon','Gambia','Georgia',
                        'Germany','Ghana','Gibraltar','Greece','Greenland','Grenada','Guadeloupe','Guam','Guatemala',
                        'Guernsey','Guinea','Guinea-Bissau','Guyana','Haiti','Heard Island and McDonald Islands','Holy See',
                        'Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran (Islamic Republic of)','Iraq',
                        'Ireland','Isle of Man','Israel','Italy','Jamaica','Japan','Jersey','Jordan','Kazakhstan','Kenya',
                        'Kiribati','Korea (Democratic People''s Republic of)','Korea','Kuwait','Kyrgyzstan',
                        'Lao People''s Democratic Republic','Latvia','Lebanon','Lesotho','Liberia','Libya',
                        'Liechtenstein','Lithuania','Luxembourg','Macao','Madagascar','Malawi','Malaysia','Maldives',
                        'Mali','Malta','Marshall Islands','Martinique','Mauritania','Mauritius','Mayotte','Mexico',
                        'Micronesia (Federated States of)','Moldova','Monaco','Mongolia','Montenegro','Montserrat',
                        'Morocco','Mozambique','Myanmar','Namibia','Nauru','Nepal','Netherlands','New Caledonia',
                        'New Zealand','Nicaragua','Niger','Nigeria','Niue','Norfolk Island','North Macedonia',
                        'Northern Mariana Islands','Norway','Oman','Pakistan','Palau','Palestine','Panama','Papua New Guinea',
                        'Paraguay','Peru','Philippines','Pitcairn','Poland','Portugal','Puerto Rico','Qatar','R\u00e9union',
                        'Romania','Russian Federation','Rwanda','Saint Barth\u00e9lemy','Saint Helena','Saint Kitts and Nevis',
                        'Saint Lucia','Saint Martin (French part)','Saint Pierre and Miquelon','Saint Vincent and the Grenadines',
                        'Samoa','San Marino','Sao Tome and Principe','Saudi Arabia','Senegal','Serbia','Seychelles','Sierra Leone',
                        'Singapore','Sint Maarten (Dutch part)','Slovakia','Slovenia','Solomon Islands','Somalia',
                        'South Africa','South Georgia and the South Sandwich Islands','South Sudan','Spain','Sri Lanka',
                        'Sudan','Suriname','Svalbard and Jan Mayen','Sweden','Switzerland','Syrian Arab Republic','Taiwan',
                        'Tajikistan','Tanzania','Thailand','Timor-Leste','Togo','Tokelau','Tonga','Trinidad and Tobago',
                        'Tunisia','Turkey','Turkmenistan','Turks and Caicos Islands','Tuvalu','Uganda','Ukraine','United Arab Emirates',
                        'United Kingdom of Great Britain and Northern Ireland','United States of America','United States Minor Outlying Islands',
                        'Uruguay','Uzbekistan','Vanuatu','Venezuela (Bolivarian Republic of)','Viet Nam','Virgin Islands (British)',
                        'Virgin Islands (U.S.)','Wallis and Futuna','Western Sahara','Yemen','Zambia','Zimbabwe']
        countryabvr = ['AF','AX','AL','DZ','AS','AD','AO','AI','AQ','AG','AR','AM','AW','AU','AT','AZ','BS','BH','BD','BB','BY','BE',
                        'BZ','BJ','BM','BT','BO',' Sint Eustatius and Saba','BA','BW','BV','BR','IO','BN','BG','BF','BI','CV','KH','CM',
                        'CA','KY','CF','TD','CL','CN','CX','CC','CO','KM','CG',' Democratic Republic of the','CK','CR','CI','HR','CU',
                        'CW','CY','CZ','DK','DJ','DM','DO','EC','EG','SV','GQ','ER','EE','SZ','ET','FK','FO','FJ','FI','FR','GF','PF',
                        'TF','GA','GM','GE','DE','GH','GI','GR','GL','GD','GP','GU','GT','GG','GN','GW','GY','HT','HM','VA','HN','HK',
                        'HU','IS','IN','ID','IR','IQ','IE','IM','IL','IT','JM','JP','JE','JO','KZ','KE','KI','KP',' Republic of','KW',
                        'KG','LA','LV','LB','LS','LR','LY','LI','LT','LU','MO','MG','MW','MY','MV','ML','MT','MH','MQ','MR','MU','YT',
                        'MX','FM',' Republic of','MC','MN','ME','MS','MA','MZ','MM','NA','NR','NP','NL','NC','NZ','NI','NE','NG','NU',
                        'NF','MK','MP','NO','OM','PK','PW',' State of','PA','PG','PY','PE','PH','PN','PL','PT','PR','QA','RE','RO','RU',
                        'RW','BL',' Ascension and Tristan da Cunha','KN','LC','MF','PM','VC','WS','SM','ST','SA','SN','RS','SC','SL','SG',
                        'SX','SK','SI','SB','SO','ZA','GS','SS','ES','LK','SD','SR','SJ','SE','CH','SY','Province of China','TJ',
                        ' United Republic of','TH','TL','TG','TK','TO','TT','TN','TR','TM','TC','TV','UG','UA','AE','GB','US','UM','UY',
                        'UZ','VU','VE','VN','VG','VI','WF','EH','YE','ZM','ZW']
        
        if self.country in countryabvr:
            return fullcountry[countryabvr.index(self.country)]
        else: return ''
    
    def _distance(self,a:Airport) -> float:
        if not isinstance(a,Airport): return None
        return round(distance.distance((float(self.lat),float(self.lon)),(float(a.lat),float(a.lon))).nautical,2)

    def _heading(self,a:Airport) -> float:
        if not isinstance(a,Airport): return None
        d = Geodesic.WGS84.Inverse(float(self.lat),float(self.lon),float(a.lat),float(a.lon))
        h = d['azi1']
        if h < 0: h=h+360.0
        return round(h,2)

    def _closest_runway_2_destination_heading(self,a:Airport) -> tuple:
        if not isinstance(a,Airport): return None
        if not self.runways: return None
        h = self._heading(a=a)
        d = 400.0
        oh = 400.0
        k = ''
        v = ''
        for key,value in self.runways.items():
            myh = float(value['heading'])
            myh2 = float(value['heading'])-180
            if myh2<0:myh2=myh2+360
            if abs(myh-h) > 180.0: myh_ = 360-abs(myh-h)
            else: myh_ = abs(myh-h)
            if abs(myh2-h) > 180.0: myh2_ = 360-abs(myh2-h)
            else: myh2_ = abs(myh2-h)
            if myh_ < d:
                k = key
                v = value
                d = myh_
                oh = myh
            elif myh2_ < d:
                k = key
                v = value
                d = myh2_
                oh = myh2
        if d==400.0: return None
        return oh,k,v

    def get_large_airports() -> list:
        return [item['ident'] for item in Airport.__airport_collection.find({'type': 'large_airport'})]

    def get_all_ident() -> list:
        return [item['ident'] for item in Airport.__airport_collection.find()]

