import os
import random
import string
from datetime import *
from pymongo import MongoClient
import pytz
import json
import bcrypt
CONTENT_TYPE_DICT = {'html': b'Content-Type: text/html;charset=UTF-8',
                           'js': b'Content-Type: text/javascript;charset=UTF-8',
                           'jpg': b'Content-Type: image/jpeg',
                           'png': b'Content-Type: image/png',
                           'css':b'Content-Type: text/css;charset=UTF-8'}

HTTPVERSION = b'HTTP/1.1'
SPACE = b' '
CRLF = b'\r\n'
NOSNIFF = b'X-Content-Type-Options: nosniff'
WORKDIR = os.getcwd()
TOKENSALT = None
chatMessagesDb = MongoClient('localhost',27017)['ChatMessages']
def parseEndpoint(request,responseBufferIn):
    ENDPOINT_DICT = {'/chat-message': chatMessage,
                 '/chat-history': chatHistory,
                 '/register': register,
                 '/login':login}
    if request.path.__contains__('/chat-message') and request.method == 'DELETE':
        return chatMessageDelete(request,responseBufferIn)
         
    return ENDPOINT_DICT[request.path](request,responseBufferIn)
    
def blankEndpoint(requestIn,responseBufferIn):
    global chatMessagesDb
    responsebody = b""

    #code 

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF

    responseBufferIn += CRLF + responsebody
    return responseBufferIn

def chatMessageDelete(requestIn,responseBufferIn):
    global chatMessagesDb
    chatMessagesCol = chatMessagesDb['messages']
    responsebody = b""

    #Get message id to delete
    id = requestIn.path.split('/')[2]
    deleted = chatMessagesCol.delete_one({'id':int(id)})

    

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF

    responseBufferIn += CRLF + responsebody
    return responseBufferIn
def login (requestIn,responseBufferIn):
    global chatMessagesDb
    responsebody = b""
    cookies = b''
    loginsCollection = chatMessagesDb['logins']
    rawLogin = dict(subString.split('=') for subString in requestIn.body.split('&'))
    
    possibleUsers = loginsCollection.find({'username':rawLogin['username_login']})
    for user in possibleUsers:
        if user['passwordHash'] ==  bcrypt.hashpw(rawLogin['password_login'].encode(),user['salt']):
            found = True
            print(F'USER AUTHENTICATED')
            #get tokens collection
            tokensCollection = chatMessagesDb['tokens']

            #gen token
            randomToken = ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))
            
            #Set expiration date of auth token to 1 hour in futue
            expiration = (pytz.timezone('US/Eastern').localize(datetime.now()) +
                           timedelta(hours=7))

            salt = TOKENSALT

            #store user,token, salt, and expiration in database
            tokensCollection.insert_one({'username':user['username'],
                                         'token': bcrypt.hashpw(randomToken.encode(),TOKENSALT)
                                         })
            #set token as cookie   
            cookies = setCookie(cookies,
                                {'token': randomToken,'Expires':expiration.strftime("%a, %d %b %Y %H:%M:%S GMT")},
                                ['Secure','HttpOnly'])


    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF + cookies + CRLF

    responseBufferIn += CRLF + responsebody
    return responseBufferIn
def register(requestIn,responseBufferIn):
    responsebody = b""
    global chatMessagesDb
    loginsCollection = chatMessagesDb['logins']
    rawLogin = dict(subString.split('=') for subString in requestIn.body.split('&'))

    login = {'username':rawLogin['username_reg'],
             'salt':bcrypt.gensalt(),
             'passwordHash':None}
    login['passwordHash'] = bcrypt.hashpw(rawLogin['password_reg'].encode(),login['salt'])
    id = loginsCollection.insert_one(login)
    

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF

    #body
    responseBufferIn += CRLF + responsebody
    return responseBufferIn

def replaceDangeChar(input):
    return input.replace('&','&amp').replace('<','&lt').replace('>','&gt')
    # while i < lent:
    #     if input[i] == '&':
    #         # if i == 0: i+=1
    #         if i == len(input): i-=1
    #         input = input[:i] + '&amp' + input[i+1:]
    #         i+=len('&amp')
    #         lent += len('&amp')
    #     elif input[i] == '<':
    #         # if i == 0: i+=1
    #         if i == len(input): i-=1
    #         input = input[:i] + '&lt' + input[i+1:]
    #         i+=len('&lt')
    #         lent += len('&lt')
    #     elif input[i] == '>':
    #         # if i == 0: i+=1
    #         if i == len(input): 
    #             i-=1
    #             input = input[:i] + '&gt'
    #         else:
    #             input = input[:i] + '&gt' + input[i+1:]
    #         i+=len('&gt')
    #         lent += len('&gt')
    #     i+=1
    
    # return input
        
def chatMessage(requestIn,responseBufferIn):
    global chatMessagesDb,numMessages
    
    messageCollection = chatMessagesDb['messages']
    tokenCollection = chatMessagesDb['tokens']
    numMessagesCollection = chatMessagesDb['numMessages']
    numMessages = list(numMessagesCollection.find())[0]['numMessages']
    username = 'Guest'
    #insert request.nessage  into database as ID | GUEST | MESSAGE 
    responsebody = b""

    #check if user is authenticated
    cookies = getCookies(requestIn)
    if cookies != None and cookies.keys().__contains__('token'):
        #check if hashed token  existws
        tokenMatches = list(tokenCollection.find({'token':(bcrypt.hashpw(cookies['token'].encode(),TOKENSALT))}))
        if len(tokenMatches) > 0:
            username = tokenMatches[0]['username']
        print(f'NUM TOKEN MATCHES: {len(tokenMatches)}')

        

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF
    message =  requestIn.body.split(b':')[1].strip(b'}').strip(b'\"')
    
    messageInsert = {'id': numMessages,
                     'username': username,
                     'message': message.decode()}
    id = messageCollection.insert_one(messageInsert)
    numMessagesCollection.update_one({'numMessages': numMessages},{'$set': {'numMessages':numMessages+1}})
    # if requestIn.body != b'':
    #     print(requestIn.body)
    #Response   
    responseBufferIn += CRLF

    #Body
    responseBufferIn+= responsebody
    return responseBufferIn
def chatHistory(requestIn,responseBufferIn):
    global chatMessagesDb
    keysToExtract = {'id':None,'username':None,'message':None}
    messages = chatMessagesDb['messages']
    cursor = messages.find()
    #ex = cursor.fromkeys(keysToExtract)
    messageHistory = []
    #for key in keysToExtract:
    #    messageHistory[messages].append(keysToExtract)
    i = 0
    for ele in cursor:
        message = {}
        for key in keysToExtract.keys():
            if key == 'message':
                ele[key] = replaceDangeChar(ele[key])
            message[key] = ele[key]          
        messageHistory.append(message)
        i+=1

    responsebody = json.dumps(messageHistory).encode()

    #for all messages in database
    #append message as JSON object to responseBody
    #Headers
    responseBufferIn += b"Content-Type: application/json" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF 

    
    #Response   
    responseBufferIn += CRLF
    #Body
    responseBufferIn+= responsebody
    return responseBufferIn

#appends set cookie directive  to buffer with specified cookies and one key value pair
def setCookie(bufferIn,cookiePairs,flags=None):
    if flags == None:
        bufferIn += b'Set-Cookie: '
        for key in cookiePairs.keys():
            if key == list(cookiePairs.keys())[0]:
                bufferIn += key.encode() + b'='+ str(cookiePairs[key]).encode()
            else:
                bufferIn+=b'; '
                bufferIn += key.encode() + b'='+ str(cookiePairs[key]).encode()
    elif flags != None :
        bufferIn += b'Set-Cookie: '
        for key in cookiePairs.keys():
            if key == list(cookiePairs.keys())[0]:
                    bufferIn += key.encode() + b'='+ str(cookiePairs[key]).encode()
            else:
                bufferIn+=b'; '
                bufferIn += key.encode() + b'='+ str(cookiePairs[key]).encode() 
        for flag in flags:
            bufferIn += b'; ' + flag.encode()  
    bufferIn+= CRLF
    return bufferIn

#gets and returns all cookies in a dictionary. If there are no cookies, returns None. 
def getCookies(requestIn):
    # if requestIn.headers['Cookie'].__contains__(';'):
    #     cookiesDict = dict(subString.split('=') for subString in requestIn.headers['Cookie'].split('; '))
    
    #only one cookie
    # else:
    #     try:
    #         onlyCookie = requestIn.headers['Cookie'].split('=')
    #         cookiesDict = dict({onlyCookie[0]:onlyCookie[1]})
    #     except IndexError:
    #         cookiesDict = None
    
    # return cookiesDict
    if requestIn.headers.keys().__contains__('Cookie'):
        cookies = requestIn.headers['Cookie']
        cookieArr = cookies.split('; ')
        cookieDict = {}
        for cookie in cookieArr:
            if cookie.__contains__('='):
                splitPair= cookie.split('=')
                cookieDict[splitPair[0]] =splitPair[1]
            else:
                cookieDict[cookie] = None
        return cookieDict
    else: return None
        


def path2ContentType(filepath: str) -> bytes:
        out = b''
        extension = filepath.split(".")[1]
        try : 
            return CONTENT_TYPE_DICT[extension]
        
        except KeyError:
            print("ERROR: UNREGISTERED FILE TYPE")
            return b"ERROR"
ENDPOINT_DICT = {'/chat-message': chatMessage,
                 '/chat-history': chatHistory,
                 '/register': register,
                 '/login':login}