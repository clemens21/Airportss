#C:\ProgramData\Microsoft\Windows\Start Menu\Programs\"Python 3.7" python


import pymongo
import pdb

class MongoDB_Client:

    client = ''
    db = ''
    isclient = False
    username = ''
    
    def __init__(self,username: str,password: str):
        if MongoDB_Client.isclient: pass
        MongoDB_Client.isclient = True
        MongoDB_Client.client = pymongo.MongoClient("*******************")
        MongoDB_Client.db = MongoDB_Client.client["AirSim_MDB"]
        MongoDB_Client.username = username
        

    def close_mongodb_install():
        MongoDB_Client.client.close()
        try: 
            MongoDB_Client.client.admin.command('ismaster')
            return False
        except: return True

    def get_client(self):
        return MongoDB_Client.client

    def get_db():
        return MongoDB_Client.db
