import bcrypt
import pymongo
class Database:
    
    def __init__(self,db_name: str, host: str, port: int):
        self.client = pymongo.MongoClient(host,port)
        
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
        self.collections = {'tokens':self.db['tokens'],
                            'messages':self.db['messages'],
                            'logins':self.db['logins'],
                            'tokens':self.db['tokens'],
                            'ProfilePictures':self.db['ProfilePictures'],
                            'numMessages':self.db['numMessages']}
        #check if token salt is generated, do so if not
        tokenSaltCol = self.db['tokensalt']
        salt = list(tokenSaltCol.find())
        if len(salt) == 0:
            self.TOKENSALT = bcrypt.gensalt()
            tokenSaltCol.insert_one({'salt':self.TOKENSALT})
        else:
            self.TOKENSALT = salt[0]['salt']
            
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
        list = [cursor]
        # for ele in cursor:
        #     document = {}
        #     for key in ele.keys():
        #         document[key] = ele[key]
        #     list.append(document)
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