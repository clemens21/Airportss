#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python

'''
Query Airport data.  No need for classes because you are not editing airports
'''

from mongodb_manager import MongoDB_Client
from typing import TypeVar
import pdb
import random
from airports import Airport
import string
import pickle
from bson.binary import Binary

# dharris
# bigd7.952mm
# create Staff classes (pilot, engineer, flight attendent, gate attendent?, baggage agent?)

# Bring in custom class type
Airplane = TypeVar('Airplane')

class Airplane:

    # Private variables
    __max_engine_condition = 100.0
    __max_airframe_condition = 100.0
    __public_airplanes_collection = ''

    def __init__(self,name_='',id_='',custom_location='') -> Airplane:
        '''
        Initializes all the stuff fr.
        Its the most important part for Airplanes... I think
        '''

        # Pass if stupid
        if not (name_ or id_): pass

        # Create and/or get collection
        if not Airplane.__public_airplanes_collection:
            Airplane.__public_airplanes_collection = MongoDB_Client.db["public_airplanes"]
        airplane_collection = MongoDB_Client.db["airplanes"]

        # If given id
        if id_:
            for data in airplane_collection.find({'_id': id_}): data=data
            # If found nothing
            if not data: pass
        # If given name
        elif name_:
            for data in airplane_collection.find({'name': name_}): data=data
            # If found nothing
            if not data: pass
        else: pass
        
        # Get info collected during web scrapping
        self.name = data['name']
        self.country = data['info']['country']
        self.description = data['info']['description']
        self.manufactured = data['info']['manufactured']
        self.manufacturer = data['info']['manufacturer']
        self.icao = data['info']['icao']
        self.price = data['info']['price_usd']
        self.url = data['info']['url']
        self.avionics = data['info']['avionics']
        self.engine = data['info']['engine']
        self.cruise_speed = data['info']['cruise_speed_knots']
        self.approach_speed = data['info']['approach_speed_knots']
        self.range = data['info']['range_nm']
        self.fuel_use_nm_g = data['info']['fuel_economy_nm_per_g']
        self.ceiling = data['info']['ceiling_ft']
        self.climb_rate = data['info']['climb_rate_ft_per_s']
        self.take_off_distance = data['info']['take_off_d_ft']
        self.landing_distance = data['info']['landing_d_ft']
        self.mtow = data['info']['mtow_lbs']
        self.mlw = data['info']['mlw_lbs']
        self.max_payload = data['info']['max_payload_lbs']
        self.fuel_cap_g = data['info']['fuel_capacity_g']
        self.baggage_volume = data['info']['baggage_volume_ft3']
        self.fuel_cap_lbs = data['info']['fuel_capacity_lbs']
        self.fuel_use_lbs_h = data['info']['fuel_economy_lbs_per_h']
        self.max_economy = data['info']['max_economy_seats']
        self.max_business = data['info']['max_business_seats']
        self.max_first = data['info']['max_first_seats']
        self.length = data['info']['length_ft']
        self.height = data['info']['height_ft']
        self.wing_span = data['info']['wing_span_ft']
        self.type = data['type']
        self.use = data['use']
        self.sim = data['sim']

        # If airplane is not released, pass
        if not bool(self.use): pass

        ###### Variables not in web scrapping #####

        # Set dry weight
        self.dry_weight = str(round(float(self.mtow) - float(self.max_payload) - float(self.fuel_cap_lbs) * 1.4,1))

        # Retrun True if you need a copilot
        self.need_copilot = '0'
        if float(self.mtow) > 20000.0: self.need_copilot = '1'

        # Return current ICAO location. On init, it sets all departure and arrival to location
        self.location = ''
        if not custom_location:
            # Get random location from all large airports
            self.location = random.choice(Airport.get_large_airports())
        else:
            if custom_location in Airport.get_all_ident():
                # Get custom location if user buys new plane
                self.location = Airport(ident_=custom_location)
            else:
                # If not a real airport, get random location from all large airports
                self.location = random.choice(Airport.get_large_airports())
        self.departure = self.location
        self.arrival = self.location

        # Initialize staff list
        self.staff = []

        # Get unique registration. Used as primary ID for planes
        tempstr = 'N'+str(random.randint(1,9))+random.choice(string.ascii_uppercase+string.digits)+random.choice(string.ascii_uppercase+string.digits)+random.choice(string.ascii_uppercase+string.digits)+random.choice(string.ascii_uppercase+string.digits)
        listofairplanes = [item['_id'] for item in Airplane.__public_airplanes_collection.find()]
        while tempstr in listofairplanes:
            tempstr = 'N'+str(random.randint(1,9))+random.choice(string.ascii_uppercase+string.digits)+random.choice(string.ascii_uppercase+string.digits)+random.choice(string.ascii_uppercase+string.digits)+random.choice(string.ascii_uppercase+string.digits)
        self.registration = tempstr

        # Set new airplane conditions. %,%,hours,hours
        self.airframe_condition = '100.0'
        self.engine_condition = '100.0'
        self.airframe_time = '0.0'
        self.flight_hours_from_inspection = '100.0'

        # Set max_airframe time based on airplane type
        if 'sepl' == self.type: self.max_airframe_time = '10000.0'
        elif 'mepl' == self.type: self.max_airframe_time = '20000.0'
        elif 'setl' == self.type: self.max_airframe_time = '25000.0'
        elif 'metl' == self.type: self.max_airframe_time = '33000.0'
        elif 'sjet' == self.type: self.max_airframe_time = '35000.0'
        elif 'mjet' == self.type: self.max_airframe_time = '44000.0'
        elif 'ljet' == self.type: self.max_airframe_time = '50000.0'
        elif 'hjet' == self.type: self.max_airframe_time = '60000.0'
        else: pdb.set_trace()
        
        # Set new plane owner,renter,loaner
        if MongoDB_Client.username == 'clemensm': self.owner = 'System'
        else: self.owner = MongoDB_Client.username
        self.renter = ''
        self.loaner = ''
        self.selling = ('0','-99999.0')

        # Set fees
        self.yearly_checkup_price = str(round(float(self.price) / 15.0,2))
        self.weekly_fee_price = str(round(float(self.price) / 365.0,2))
        self.engine_price = str(round(float(self.price) / 300.0,2))
        self.airframe_price = str(round(float(self.price) / 300.0,2))

        # Set seats and max payload
        self.economy = '0'
        self.business = '0'
        self.first = '0'
        self.available_cargo_weight = self.max_payload

        # Set passengers
        self.passengers = ('0','0','0')

        # Set fuel gallons
        self.available_fuel = self.fuel_cap_g

    def create_airplane(p: Airplane) -> None:
        '''Add a new airplane to mongodb public_airplanes collection'''
        Airplane.__public_airplanes_collection.insert_one({'_id': p.registration,'owner': p.owner,'renter': p.renter,'loaner': p.loaner,'plane': Binary(pickle.dumps(p))})

    def update_airplane(p: Airplane) -> None:
        '''Update airplane in mongodb public_airplanes collection'''
        Airplane.__public_airplanes_collection.update_one({'_id': p.registration},{'$set': {'owner': p.owner,'renter': p.renter,'loaner': p.loaner,'plane': Binary(pickle.dumps(p))}})

    def pull_airplane(registration: str) -> Airplane:
        '''Pull airplane from mongodb public_airplanes collection'''
        p = Airplane.__public_airplanes_collection.find_one({'_id': registration})
        return pickle.loads(p['plane'])
    
    def pull_all_user_planes(user: str) -> list:
        '''Pull all airplanes based on user name from mongodb public_airplanes collection'''
        out = []
        ps = Airplane.__public_airplanes_collection.find({'owner': user})
        for item in ps:
            out.append(pickle.loads(item['plane']))
        ps = Airplane.__public_airplanes_collection.find({'renter': user})
        for item in ps:
            out.append(pickle.loads(item['plane']))
        ps = Airplane.__public_airplanes_collection.find({'loaner': user})
        for item in ps:
            out.append(pickle.loads(item['plane']))
        return out

    def _can_takeoff_from_airport_length(self,a: Airport) -> bool:
        '''Can the plane takeoff at a given airport'''
        l,_,_ = a._max_landing_length()
        tod = self.__gettakeoffdistance__()
        if tod > 0:
            if l >= tod: return 1
            else:  return 0
        else: return 1

    def _can_takeoff_weight(self) -> bool:
        
        myweight = (float(self.available_fuel) * 6.67) + (float(self.max_payload) - float(self.available_cargo_weight)) + float(self.dry_weight)
        if self.mtow > myweight: return 1
        else: return 0

    def _can_land_at_airport_length(self,a: Airport) -> bool:
        '''Can the plane land at a given airport'''
        l,_,_ = a._max_landing_length()
        if self.landing_distance:
            if l >= float(self.landing_distance): return 1
            else: return 0
        else: return 1

    def _how_long_is_flight_time(self,a1: Airport,a2: Airport) -> str:
        '''How long is the flight time in hours'''
        d = a1._distance(a2)
        buffer = 1.02
        return str(round(d/float(self.cruise_speed)*buffer,1))

    def _how_far_can_plane_travel(self) -> str:
        buffer = 1.0
        return str(round(float(self.available_fuel) * float(self.fuel_use_nm_g) * buffer,1))

    def _update_passengers(self,t=(0,0,0)) -> Airplane:
        '''Update self.passengers and self.available_cargo_weight'''
        passenger_weight = 180.0
        total_passengers_old = sum(self.passengers)
        total_passengers_new = sum(t)
        self.passengers = t
        if total_passengers_new > total_passengers_old:
            self.available_cargo_weight = self.available_cargo_weight - (passenger_weight*total_passengers_new)
        elif total_passengers_new < total_passengers_old:
            self.available_cargo_weight = self.available_cargo_weight + (passenger_weight*total_passengers_new)
        else:
            self.available_cargo_weight = self.available_cargo_weight
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_engine_condition(self,p: float) -> Airplane:
        '''Update self.engine_condition'''
        self.engine_condition = round(self.engine_condition - p,1)
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_airframe_time(self,t: float) -> Airplane:
        '''Update self.airframe_time'''
        self.airframe_time = round(self.airframe_time + t)
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_owner(self,o: str) -> Airplane:
        '''Update self.owner'''
        self.owner = o
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_loaner(self,o: str) -> Airplane:
        '''Update self.lowner'''
        self.renter = ''
        self.loaner = o
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_renter(self,o: str) -> Airplane:
        '''Update self.renter'''
        self.renter = o
        self.loaner = ''
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_location(self,l: str) -> Airplane:
        '''Update self.location'''
        self.location = l
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_departure_arrival(self,l1: str,l2: str) -> Airplane:
        '''Update self.departure and self.arrival'''
        self.departure = l1
        self.arrival = l2
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_staff(self,s: list) -> Airplane:
        '''Update self.staff'''
        self.staff = s
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_flight_hours_from_inspection(self,h: float) -> Airplane:
        '''Update self.flight_hours_from_inspection'''
        self.flight_hours_from_inspection = round(self.flight_hours_from_inspection - h,1)
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_economy(self,s: int) -> Airplane:
        '''Update self.economy and self.available_cargo_weight'''
        seat_weight = 30
        if self.economy > s:
            self.available_cargo_weight = self.available_cargo_weight + (seat_weight*self.economy)
        elif self.economy < s:
            self.available_cargo_weight = self.available_cargo_weight - (seat_weight*self.economy)
        else:
            self.available_cargo_weight = self.available_cargo_weight
        self.economy = s
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_business(self,s: int) -> Airplane:
        '''Update self.business and self.available_cargo_weight'''
        seat_weight = 125
        if self.business > s:
            self.available_cargo_weight = self.available_cargo_weight + (seat_weight*self.business)
        elif self.business < s:
            self.available_cargo_weight = self.available_cargo_weight - (seat_weight*self.business)
        else:
            self.available_cargo_weight = self.available_cargo_weight
        self.business = s
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_first(self,s: int) -> Airplane:
        '''Update self.first and self.available_cargo_weight'''
        seat_weight = 200
        if self.first > s:
            self.available_cargo_weight = self.available_cargo_weight + (seat_weight*self.first)
        elif self.first < s:
            self.available_cargo_weight = self.available_cargo_weight - (seat_weight*self.first)
        else:
            self.available_cargo_weight = self.available_cargo_weight
        self.first = s
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def _update_available_fuel(self,g: float) -> Airplane:
        '''Update self.flight_hours_from_inspection'''
        self.available_fuel = round(self.flight_hours_from_inspection + g,1)
        Airplane.update_airplane(self)
        return Airplane.pull_airplane(self.registration)

    def __getname__(self) -> str:
        return self.name

    def __getcountry__(self) -> str:
        return self.country

    def __getdescription__(self) -> str:
        return self.description

    def __getmanufactured__(self) -> str:
        return self.manufactured

    def __getmanufacturer__(self) -> str:
        return self.manufacturer

    def __geticao__(self) -> str:
        return self.icao.upper()

    def __getprice__(self) -> float:
        return round(float(self.price),2)

    def __geturl__(self) -> str:
        return self.url

    def __getavionics__(self) -> str:
        return self.avionics

    def __getengine__(self) -> str:
        return self.engine

    def __getcruisespeed__(self) -> int:
        if self.cruise_speed: return int(self.cruise_speed.split('.')[0])
        else: return -1

    def __getapproachspeed__(self) -> int:
        if self.approach_speed: return int(self.approach_speed.split('.')[0])
        else: return -1

    def __getrange__(self) -> int:
        if self.range: return int(self.range.split('.')[0])
        else: return -1

    def __getfuelusenmg__(self) -> float:
        if self.fuel_use_nm_g: return round(float(self.fuel_use_nm_g),3)
        else: return -1.0

    def __getceiling__(self) -> int:
        if self.ceiling: return int(self.ceiling.split('.')[0])
        else: return -1

    def __getclimbrate__(self) -> int:
        if self.climb_rate: return int(self.climb_rate.split('.')[0])
        else: return -1

    def __gettakeoffdistance__(self) -> int:
        if self.take_off_distance: return int(self.take_off_distance.split('.')[0])
        else: return -1

    def __getlandingdistance__(self) -> int:
        if self.landing_distance: return int(self.landing_distance.split('.')[0])
        else: return -1

    def __getmtow__(self) -> int:
        if self.mtow: return int(self.mtow.split('.')[0])
        else: return -1

    def __getmlw__(self) -> int:
        if self.mlw: return int(self.mlw.split('.')[0])
        else: return -1

    def __getmaxpayload__(self) -> int:
        if self.max_payload: return int(self.max_payload.split('.')[0])
        else: return -1

    def __getfuelcapg__(self) -> float:
        if self.fuel_cap_g: return round(float(self.fuel_cap_g),2)
        else: return -1.0

    def __getbaggagevolume__(self) -> int:
        if self.baggage_volume: return int(self.baggage_volume.split('.')[0])
        else: return -1

    def __getfuelcaplbs__(self) -> float:
        if self.fuel_cap_lbs: return round(float(self.fuel_cap_lbs),2)
        else: return -1.0

    def __getfueluselbsh__(self) -> float:
        if self.fuel_use_lbs_h: return round(float(self.fuel_use_lbs_h),2)
        else: return -1.0

    def __getmaxeconomy__(self) -> int:
        if self.max_economy: return int(self.max_economy.split('.')[0])
        else: return -1

    def __getmaxbusiness__(self) -> int:
        if self.max_business: return int(self.max_business.split('.')[0])
        else: return -1

    def __getmaxfirst__(self) -> int:
        if self.max_first: return int(self.max_first.split('.')[0])
        else: return -1

    def __getlength__(self) -> int:
        if self.length: return int(self.length.split('.')[0])
        else: return -1

    def __getheight__(self) -> int:
        if self.height: return int(self.height.split('.')[0])
        else: return -1

    def __getwingspan__(self) -> int:
        if self.wing_span: return int(self.wing_span.split('.')[0])
        else: return -1

    def __gettype__(self) -> str:
        return self.type.upper()

    def __getuse__(self) -> bool:
        return bool(int(self.use))

    def __getsim__(self) -> list:
        return [k for k in self.sim.keys()]

    def __getdryweight__(self) -> int:
        if self.dry_weight: return int(self.dry_weight.split('.')[0])
        else: return -1

    def __getneedcopilot__(self) -> bool:
        return bool(int(self.need_copilot))

    def __getlocation__(self) -> str:
        return self.location.upper()

    def __getdeparture__(self) -> str:
        return self.departure.upper()

    def __getarrival__(self) -> str:
        return self.arrival.upper()

    def __getstaff__(self) -> list:
        return self.staff

    def __getregistration__(self) -> str:
        return self.registration

    def __getairframecondition__(self) -> float:
        return round(float(self.airframe_condition),2)

    def __getenginecondition__(self) -> float:
        return round(float(self.engine_condition),2)

    def __getairframetime__(self) -> float:
        return round(float(self.airframe_time),2)

    def __getflighthoursfrominspection__(self) -> float:
        return round(float(self.flight_hours_from_inspection),2)

    def __getmaxairframetime__(self) -> int:
        return int(self.max_airframe_time.split('.')[0])

    def __getowner__(self) -> str:
        return self.owner

    def __getrenter__(self) -> str:
        return self.renter

    def __getloaner__(self) -> str:
        return self.loaner

    def __getselling__(self) -> tuple:
        return (bool(int(self.selling[0])),float(self.selling[0]))

    def __getyearlycheckupprice__(self) -> float:
        return round(float(self.yearly_checkup_price),2)

    def __getweeklyfeeprice__(self) -> float:
        return round(float(self.weekly_fee_price),2)

    def __getengineprice__(self) -> float:
        return round(float(self.engine_price),2)

    def __getairframeprice__(self) -> float:
        return round(float(self.airframe_price),2)

    def __getfirst__(self) -> int:
        return int(self.first.split('.')[0])

    def __getbusiness__(self) -> int:
        return int(self.business.split('.')[0])

    def __geteconomy__(self) -> int:
        return int(self.economy.split('.')[0])

    def __getavailablecargoweight__(self) -> int:
        return int(self.available_cargo_weight.split('.')[0])

    def __getpassengers__(self) -> tuple:
        return (int(self.passengers[0]),int(self.passengers[1]),int(self.passengers[2]))

    def __getavailablefuel__(self) -> float:
        return round(float(self.available_fuel),2)