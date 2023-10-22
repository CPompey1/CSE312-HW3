import pymongo
class Database:
    
    def __init__(self,db_name: str, host: str, port: int):
        self.client = pymongo.MongoClient(host,port)
        self.collections = {}
        serverStarted = False
        while not serverStarted:
            try:
                with pymongo.timeout(5):
                    self.client.list_database_names()
                serverStarted = True
                self.db = self.client[db_name]
            except pymongo.errors.ServerSelectionTimeoutError:
                #start database 
                print('Server not started')
                
    def createCollection(self,name :str):
        self.collections[name] = self.client[name]
        
    def insertOne(self,collection: str, data: dict):
        self.collections[collection].insert_one(data)
        
    def findAll(self,collection: str):
        return self.collections[collection].find()
    
    def findOne(self,collection: str,keysToSearch: dict):
        return self.collections[collection].find_one(keysToSearch)
    
    def findOne_asList(self,collection: str,keysToSearch: dict):
        cursor = self.collections[collection].find_one()
        list = []
        for ele in cursor:
            document = {}
            for key in ele.keys():
                document[key] = ele[key]
            list.append(document)
        return list
    
    def findAll_asList(self,collection: str, data: dict):
        cursor = self.collections[collection].find()
        list = []
        for ele in cursor:
            document = {}
            for key in ele.keys():
                document[key] = ele[key]
            list.append(document)
        return list