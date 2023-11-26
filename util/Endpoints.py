import base64
import hashlib
import os
import random
import string
from datetime import *
from pymongo import MongoClient
import pytz
import json
import bcrypt
from util.Global import *
from util.Helpers import *
import threading
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
ENDPOINT_DICT = None
chatMessagesDb = MongoClient('localhost',27017)['ChatMessages']
def parseEndpoint(tcpHandler,request,responseBufferIn):
    if request.path.__contains__('chat-message') and request.method == 'DELETE':
        return chatMessageDelete(tcpHandler,request,responseBufferIn)
    if 'websocket' in request.path:
        ENDPOINT_DICT[request.path.strip('/')](tcpHandler,request,responseBufferIn)
    else:
        return ENDPOINT_DICT[request.path.strip('/')](tcpHandler,request,responseBufferIn)
    

def computeKey(key):
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    #append guid for websockets
    key += GUID

    #hash key
    hashedKey = hashlib.sha1(key.encode()).hexdigest()

    #base64 encode key
    base64Encoded = base64.b64encode(bytes.fromhex(hashedKey)).decode()
    return base64Encoded
def initWebsocket(tcpHandler,requestIn, responseBufferIn):
    responsebody = b""
    tokenCollection = DB.collections['tokens']
    username = 'Guest'
    print("Suck up ya bumbaclaugt")

    #check if user is authenticated
    cookies = getCookies(requestIn)
    if cookies != None and cookies.keys().__contains__('token'):
        #check if hashed token  existws
        tokenMatches = list(tokenCollection.find({'token':(bcrypt.hashpw(cookies['token'].encode(),DB.TOKENSALT))}))
        if len(tokenMatches) > 0:
            username = tokenMatches[0]['username']
        print(f'NUM TOKEN MATCHES: {len(tokenMatches)}')

    #Get websocket key
    key = requestIn.headers['Sec-WebSocket-Key']
    
    #set key in cookie of response
    computedKey = computeKey(key)
    cookie = setCookie(b'',{'Sec-WebSocket-Accept':computedKey})
    
    

    #Headers
    responseBufferIn += b"101" + SPACE + b"Switching Protocols" + CRLF
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += b'Connection: Upgrade' + CRLF
    responseBufferIn += b'Upgrade: websocket' + CRLF
    responseBufferIn += b'Sec-WebSocket-Accept: ' + computedKey.encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF  

    #body
    responseBufferIn += CRLF + responsebody
    
    print(responseBufferIn)
    #send accept request response
    tcpHandler.request.send(responseBufferIn)
    
    # t = threading.Thread(target=handleChatWSFrames,args=(tcpHandler,username))
    # t.start()
    #handle websocket 
    handleChatWSFrames(tcpHandler,username)
def profilePic(tcpHandler,requestIn,responseBufferIn):
    responsebody = b""

    #code 
    #authenticate
    authenticateOutput = authenticate(requestIn)
    if authenticateOutput == None:
        responsebody = b'Must be logged in'
    else:
        user,token = authenticateOutput
        picBytes = requestIn.body
        fileName = requestIn.headerFlags['Content-Disposition']['filename'].strip("\"").strip("\'")
        fullFileName = f'{user}_{fileName}'
        with open(f'{os.getcwd()}/public/image/{fullFileName}','wb') as file:
            file.write(picBytes)
        DB.insertOne('ProfilePictures',{'username':user,
                                        'Profile_picture_name': fullFileName})
        responsebody = b'Succesfully uploaded image'

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF

    responseBufferIn += CRLF + responsebody
    tcpHandler.request.send(responseBufferIn) 
def blankEndpoint(tcpHandler,requestIn,responseBufferIn):
    global chatMessagesDb
    responsebody = b""
 
    #code 

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF

    responseBufferIn += CRLF + responsebody
    tcpHandler.request.send(responseBufferIn) 

def chatMessageDelete(tcpHandler,requestIn,responseBufferIn):
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
    tcpHandler.request.send(responseBufferIn) 
def login (tcpHandler,requestIn,responseBufferIn):
    global chatMessagesDb
    responsebody = b""
    cookies = b''
    loginsCollection = chatMessagesDb['logins']
    rawLogin = dict(subString.split(b'=') for subString in requestIn.body.split(b'&'))
    
    possibleUsers = loginsCollection.find({'username':rawLogin[b'username_login'].decode()})
    for user in possibleUsers:
        if user['passwordHash'] ==  bcrypt.hashpw(rawLogin[b'password_login'],user['salt']):
            found = True
            print(F'USER AUTHENTICATED')
            #get tokens collection
            tokensCollection = chatMessagesDb['tokens']

            #gen token
            randomToken = ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))
            
            #Set expiration date of auth token to 1 hour in futue
            expiration = (pytz.timezone('US/Eastern').localize(datetime.now()) +
                           timedelta(hours=20))

            salt = DB.TOKENSALT

            #store user,token, salt, and expiration in database
            tokensCollection.insert_one({'username':user['username'],
                                         'token': bcrypt.hashpw(randomToken.encode(),DB.TOKENSALT)
                                         })
            #set token as cookie   
            cookies = setCookie(cookies,
                                {'token': randomToken,'Expires':expiration.strftime("%a, %d %b %Y %H:%M:%S GMT")},
                                ['Secure','HttpOnly'])


    #Headers
    responseBufferIn += b"200" + SPACE + b"OK" + CRLF
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF + cookies + CRLF

    responseBufferIn += CRLF + responsebody
    tcpHandler.request.send(responseBufferIn) 
def register(tcpHandler,requestIn,responseBufferIn):
    responsebody = b""
    global chatMessagesDb
    loginsCollection = chatMessagesDb['logins']
    rawLogin = dict(subString.split(b'=') for subString in requestIn.body.split(b'&'))

    login = {'username':rawLogin[b'username_reg'].decode(),
             'salt':bcrypt.gensalt(),
             'passwordHash':None}
    login['passwordHash'] = bcrypt.hashpw(rawLogin[b'password_reg'],login['salt'])
    id = loginsCollection.insert_one(login)
    

    #Headers
    responseBufferIn += b"Content-Type: text/plain" + CRLF
    responseBufferIn += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
    responseBufferIn += NOSNIFF + CRLF

    #body
    responseBufferIn += CRLF + responsebody
    tcpHandler.request.send(responseBufferIn) 

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
        
def chatMessage(tcpHandler,requestIn,responseBufferIn):
    global chatMessagesDb,numMessages
    
    messageCollection = chatMessagesDb['messages']
    tokenCollection = chatMessagesDb['tokens']
    numMessagesCollection = chatMessagesDb['numMessages']
    username = 'Guest'
    #insert request.nessage  into database as ID | GUEST | MESSAGE 
    responsebody = b""

    #check if user is authenticated
    cookies = getCookies(requestIn)
    if cookies != None and cookies.keys().__contains__('token'):
        #check if hashed token  existws
        tokenMatches = list(tokenCollection.find({'token':(bcrypt.hashpw(cookies['token'].encode(),DB.TOKENSALT))}))
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
    tcpHandler.request.send(responseBufferIn) 
def chatHistory(tcpHandler,requestIn,responseBufferIn):
    global chatMessagesDb
    keysToExtract = {'id':None,'username':None,'message':None}
    messages = chatMessagesDb['messages']
    cursor = messages.find()
    messageHistory = []
    i = 0
    for ele in cursor:
        message = {}
        for key in keysToExtract.keys():
            try:
                if key == 'message':
                    ele[key] = replaceDangeChar(ele[key])
                message[key] = ele[key]    
            except KeyError:
                print(f'ERROR: invalid document in chat messages: {ele}')      
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
    tcpHandler.request.send(responseBufferIn) 

#appends set cookie directive  to buffer with specified cookies and one key value pair or pass empty buffer to get cookie string
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
ENDPOINT_DICT = {'chat-message': chatMessage,
                 'chat-history': chatHistory,
                 'register': register,
                 'login':login,
                 'profile-pic': profilePic,
                 'websocket':initWebsocket}