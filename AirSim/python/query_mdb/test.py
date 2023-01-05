#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python

from mongodb_manager import MongoDB_Client
from airports import Airport
from airplanes import Airplane
import pdb
import pickle


# On start
MongoDB_Client(username="*******",password="*******")

kcos = Airport(ident_='KCOS')
kden = Airport(ident_='KDEN')

aa = kcos._closest_runway_2_destination_heading(kden)

myplane = Airplane(name_='Boeing 747-8 Freighter')

Airplane.create_airplane(myplane)

test = Airplane.pull_airplane(myplane.registration)

test2 = Airplane.pull_all_user_planes('clemensm')
pdb.set_trace()
MongoDB_Client.close_mongodb_install()
