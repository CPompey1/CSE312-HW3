import json
from util.Frame import Frame

class ChatSockets:
    sockets = None
    def __init__(self) -> None:
        global sockets
        sockets = []
    

    def send_to_all(self,message):
        global sockets
        for handlerDict in sockets:
            try:
                handlerDict['handler'].request.sendall(message)
            except OSError:
                print("Dead socket")
                sockets.remove(handlerDict)

    def handleChatWSFrames(self,tcpHandler,username,DB):
        global sockets
        print('Accepted ya skunt')
        emptyFrames = 0
        numMessagesCollection = DB.collections['numMessages']
        while True:
            buffer = tcpHandler.request.recv(2048)
            if len(buffer) > 0:
                print(buffer)
                frame = Frame(frame=buffer)
                if frame.opcode == Frame.CONNECTION_CLOSE_OP:
                    break
                remainingBytes = frame.payloadLen - len(frame.payload)
                if remainingBytes > 0:
                    buffer == tcpHandler.request.recv(remainingBytes)
                    frame.extend_payload(buffer)

                # Handle(insert) payload(message) (to database)
                numMessages = DB.findOne('numMessages',{})['numMessages']
                # numMessages = list(numMessagesCollection.find())[0]['numMessages']
                message = json.loads(frame.payload.decode())
                
                #send payload through websocket
                messageInsert = {'messageType': 'chatMessage',
                        'username': self.replaceDangeChar(username),
                        'message': self.replaceDangeChar(message['message']),
                        'id': numMessages}
                frame = Frame(payload=messageInsert)

                #send to all websockets
                self.send_to_all(frame.bufferToSend)

                #update db
                messageInsert = {'id': numMessages,
                        'username': username,
                        'message': message['message']}
                DB.insertOne('messages',messageInsert)

                #update num messages
                numMessagesCollection.update_one({'numMessages': numMessages},{'$set': {'numMessages':numMessages+1}})
                emptyFrames = 0
            elif emptyFrames <=10:
                emptyFrames +=1
            else:
                print("Getting empty frames, abort handling")
                break
    def handle_socket(self,tcpHandler,username,DB):
        global sockets
        handler = {'handler':tcpHandler,'username':username}
        sockets.append(handler)
        self.handleChatWSFrames(tcpHandler,username,DB)
        sockets.remove(handler)

    def replaceDangeChar(self,input):
        return input.replace('&','&amp').replace('<','&lt').replace('>','&gt')