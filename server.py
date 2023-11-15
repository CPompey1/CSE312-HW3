import socketserver
import sys
import bcrypt

from pymongo import MongoClient
import pymongo
from util.request import Request
import os
from  util import Endpoints
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
mongoClient = None
chatMessagesDb = None
class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):

        

        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        responsebuffer = b''

        #Add http version 
        responsebuffer += HTTPVERSION
        responsebuffer += SPACE
        
        try:
            if request.path == '/':
                path = f'{WORKDIR}/public{request.path}index.html'
            else:
                path = f'{WORKDIR}{request.path}'
            
            # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
            with open(path,'rb') as file:
                requestedFile = file.read()

            #Headers
            #add status line
            responsebuffer +=b'200' + SPACE + b'OK'+ CRLF
            responsebuffer += b'Content-Length: ' + str(len(requestedFile)).encode() + CRLF
            responsebuffer += NOSNIFF + CRLF
            responsebuffer += path2ContentType(path) + CRLF
            
            #Add blank line for prior to body
            responsebuffer += CRLF

            #add response body
            responsebuffer += requestedFile

            self.request.sendall(responsebuffer)
            
        except FileNotFoundError:
            visitCount = 0
            cookieHeader = b''
            #test in incognito
            if request.path.split('/')[1] in Endpoints.ENDPOINT_DICT.keys():
                responsebuffer = Endpoints.parseEndpoint(request,responsebuffer)
            # if request.path == '/visit-counter':
            #     responsebuffer = visitCounter(request,responsebuffer)
            # elif request.path == '/chat-message':
            #     responsebuffer = chatMessage(requestIn=request,responseBufferIn=responsebuffer)
            # elif request.path == '/chat-history':
            #     responsebuffer = chatHistory(requestIn=request,responseBufferIn=responsebuffer)      
            # elif request.path == '/register':
            #     responsebuffer = register(requestIn=request,responseBufferIn=responsebuffer)
            # elif request.path == '/login':
            #     responsebuffer = login(requestIn=request,responseBufferIn=responsebuffer)
            # elif request.path.__contains__('/chat-message/') and request.method == 'DELETE':
            #     responsebuffer = chatMessageDelete(requestIn=request,responseBufferIn=responsebuffer)
            else:   
                responsebody = b"404 Resource Not found"
                #stats line
                responsebuffer += b"404" + SPACE + b"NOTOK" + CRLF

                #Headers
                responsebuffer += b"Content-Type: text/plain" + CRLF
                responsebuffer += b"Content-Length: " + str(len(responsebody)).encode() + CRLF
                responsebuffer += NOSNIFF + CRLF
            
                #Response   
                responsebuffer += CRLF

                #Body
                responsebuffer+= responsebody
            self.request.sendall(responsebuffer)
            
def path2ContentType(filepath: str) -> bytes:
        out = b''
        extension = filepath.split(".")[1]
        try : 
            return CONTENT_TYPE_DICT[extension]
        
        except KeyError:
            print("ERROR: UNREGISTERED FILE TYPE")
            return b"ERROR"
def initChatMessages():
    global mongoClient 
    global chatMessagesDb
    global TOKENSALT
    global numMessages
    mongoClient = client = MongoClient('localhost',27017)
    
   
    serverStarted = False
    while not serverStarted:
        try:
            with pymongo.timeout(5):
                client.list_database_names()
            serverStarted = True
            chatMessagesDb = client['ChatMessages'] 
            Endpoints.chatMessagesDb = client['ChatMessages'] 
        except pymongo.errors.ServerSelectionTimeoutError:
            #start database 
            print('Server not started')
        
     #check if token salt is generated, do so if not
    tokenSaltCol = chatMessagesDb['tokensalt']
    salt = list(tokenSaltCol.find())
    if len(salt) == 0:
        TOKENSALT = bcrypt.gensalt()
        tokenSaltCol.insert_one({'salt':TOKENSALT})
    else:
        TOKENSALT = salt[0]['salt']
    
     #Initialize num Messages
    numMessagesCol = chatMessagesDb['numMessages']
    numMessagesList = list(numMessagesCol.find())
    if len(numMessagesList) == 0:
        numMessages = 0
        numMessagesCol.insert_one({'numMessages':numMessages})
    else:
        numMessages = numMessagesList[0]['numMessages']
        
    return 
def main():
    host = "localhost"
    port = 8081
    initChatMessages()
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    sys.stdout.flush()
    sys.stderr.flush()

    server.serve_forever()


if __name__ == "__main__":
    main()
