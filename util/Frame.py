

import json


class Frame:
    #opcode
    CONTINUATION_FRAME_OP = 0
    TEXT_FRAME_OP = 1
    BINARY_FRAME_OP = 2
    CONNECTION_CLOSE_OP = 8
     
    def __init__(self,frame = None,payload=None):
        if frame == None and payload != None:
            self.bufferToSend = b''
            #add fin bit and opcode
            self.bufferToSend += 0x81.to_bytes(length=1,byteorder="little")

            #if len(payload) < 126
            payloadLen = len(json.dumps(payload))
            print(f"Parsing last frame...")
            if payloadLen < 126:
                self.bufferToSend += (payloadLen & 0x7f).to_bytes(length=1,byteorder= "little")
            
            else:
                if payloadLen <= 0xffff:
                    #encode 126
                    self.bufferToSend += (0x7e).to_bytes(length=1,byteorder= "big")
                    #encode actual length
                    self.bufferToSend += (payloadLen).to_bytes(length=2,byteorder= "big")
                else:
                    #encode 127
                    self.bufferToSend += (0x7f).to_bytes(length=1,byteorder= "big")
                    #enode actual length
                    self.bufferToSend += (payloadLen & 0x7fffffffffffffff).to_bytes(length=8,byteorder= "big")
                # else:
                #     print("ERROR: Large  buffer not implemented")
            
            #skip masking key
            #add payload
            self.bufferToSend += json.dumps(payload).encode()
        else:
            #parse all bytes in little endian
            i = 0
            #get fin bit (final fragment in a message bit)
            temp = frame[i]
            self.finBit = (temp & 0x80 == 0x80)

            #Get op code {0=continuation frame,1=text frame,2=binary frame,8=connection close}
            self.opcode = temp & 0x0f

            if self.opcode == Frame.CONNECTION_CLOSE_OP:
                #set payload to None if opcode ==8
                print("Websocket connection closing..")
                self.payload = None
                return
            #extend payload if opcode == 0
            elif self.opcode == Frame.CONTINUATION_FRAME_OP:
                self.extend_payload(frame)
                print("continuation")
                return
            #parse initial frmae if opcode == 2
            elif self.opcode == Frame.TEXT_FRAME_OP:
                print(f"Parsing initial frame...")
            else:
                print(f"ERROR: opcode{self.opcode} is not implemented")
                self.payload = None
                return
            i+=1
            #get mask bit  (payload data is masked if sete to 1)
            temp = frame[i]        
            self.maskBit = (temp & 0x80 == 0x80)

            #get 7 bit payload length
            self.payloadLen = temp & 0x7f

            
            if self.payloadLen >= 126:
                i+=1
                if self.payloadLen == 126:
                    #payloadlength is extended by 2 byte
                    #no idea if this'll work
                    self.payloadLen = int.from_bytes(frame[i:i+2],byteorder="big") 
                    # self.payload = int.from_bytes(frame[i:i+2],byteorder="big") 
                    i+=2
                #elif payload length == 127 
                elif self.payloadLen == 127:
                    #payloadlength is extended by 8 bytes
                    # self.payload = int.from_bytes(frame[i:i+8],byteorder="big") 
                    self.payloadLen = int.from_bytes(frame[i:i+8],byteorder="big")  
                    i+=8
                else:
                    print("Error: Large  buffer not implemented")
                    self.payload == None
                    return
            else:
                i+=1
            #get masking key if mask is 1
            self.mask = b''
            if self.maskBit:
                temp = frame[i]
                for byte in frame[i:i+4]:
                    self.mask+= byte.to_bytes(1,byteorder="little")
                i+=4
            
            #get payload
            self.payload = b''
            for byte in frame[i:]:
                self.payload += byte.to_bytes(1,byteorder="little")
            
            #mask payload
            self.mask_paylad()
        
    def mask_paylad(self):
        temp = self.payload
        self.payload =  b''
        for byte,i in zip(temp,range(self.payloadLen)):
            self.payload += (byte ^ self.mask[i%4]).to_bytes(1,byteorder="little")

    def mask_in(input,mask):
        temp = input
        payload =  b''
        for byte,i in zip(temp,range(len(input))):
            payload += (byte ^ mask[i%4]).to_bytes(1,byteorder="little")
        return input
    
    
          
    def extend_payload(self,incBuffer):
        temp = self.payload
        self.payload = b''
        for byte in incBuffer:
            self.payload += byte.to_bytes(1,byteorder="big")
        self.mask_paylad()
        self.payload = temp + self.payload

    # def int_to_little_endian(byte_int_8):
    #     return int.from_bytes(byte_int_8.to_bytes(1,byteorder="big"),byteorder="big")
    
    def int_to_little_endian(byte_int_8):
        temp = b'\x01'[0]
        out = b'\x00'[0]
        while temp <= pow(2,7):
            out <<=1
            if temp & byte_int_8 == temp: 
                out ^=1
            temp<<=1 
        return out
    def bytes_to_little_endian(bytesIn):
        return 