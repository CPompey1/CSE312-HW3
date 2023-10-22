import pymongo
from Database import Database 
import bcrypt

class Account:

    def createUser(self,collectionName,username,password,otherUserElements: [] = None):
        login = {'username':username,
             'salt':bcrypt.gensalt(),
             'passwordHash':None}
        
