from util.Helpers import *
# from Helpers import *
class Request:

    def __init__(self, request: bytes,exiBuffer = None):
        # TODO: parse the bytes of the request and populate the following instance variables
        CRLF = b'\r\n'
        bytesByLine = request.split(CRLF)
        with open('requests','a') as file:
                print(request,file=file)
        if exiBuffer != None and len(request) > 0:
            i = 0
            runningLen = 0
            exiBuffer.bodyParsed = False
            if exiBuffer.headerPassed: exiBuffer.bodyLen+=len(request)
            #gonna assume only headers and body is left
            for line in bytesByLine:
                if exiBuffer.boundary != None and exiBuffer.boundary in line:
                    exiBuffer.boundaryPassed +=1
                elif line == b'' and not exiBuffer.headerPassed: #and contentype contains multipart
                        if 'Content-Type' in exiBuffer.headers.keys() and 'multipart' in exiBuffer.headers['Content-Type']:
                            exiBuffer.boundary = f"{exiBuffer.headerFlags['Content-Type']['boundary']}".encode()
                            exiBuffer.bodyLen += len(request[runningLen + len(CRLF):])
                            print('hello')
                        else: 
                            exiBuffer.headerPassed = True
                            
                elif not exiBuffer.headerPassed: # need to know how were in first part 
                        #headers
                        out = header2DictsB(line)
                        exiBuffer.headers.update(out[0])
                        exiBuffer.headerFlags.update(out[1])
                #line is raw bytes
                elif exiBuffer.headerPassed and not exiBuffer.bodyParsed:
                    exiBuffer.body += request[runningLen:]
                    if b'PNG' in line:
                        exiBuffer.body+=CRLF
                    exiBuffer.bodyParsed = True
                i+=1

                if exiBuffer.headerPassed: 
                    runningLen+=len(line)
                    exiBuffer.len += len(line)
                else:
                    runningLen += len(line) + len(CRLF)
                    exiBuffer.len += len(line) + len(CRLF)
            for classAttr in exiBuffer.__dict__.keys():
                self.__dict__[classAttr] = exiBuffer.__dict__[classAttr]
        else:
            self.body = b''
            self.method = ""
            self.path = ""
            self.http_version = ""
            self.headers = {}
            self.headerFlags = {}
            self.len= 0
            self.headerPassed = False
            numEmptyLines = 0
            self.boundaryPassed = 0
            self.boundary = None
            self.bodyParsed = False
            self.bodyLen=0
            if request.__len__()> 0:
                #debug line
                while bytesByLine[numEmptyLines] == b'':
                    numEmptyLines+=1
                # bytesByLine = bytesByLine[numEmptyLines:]
                i = 0
                for line in bytesByLine:
                    if line == bytesByLine[0] and not self.headerPassed:
                        firstLineFieleds = line.split(b' ')
                        self.method = firstLineFieleds[0].strip(b' ').decode()
                        self.path = firstLineFieleds[1].strip(b' ').decode()
                        self.http_version = firstLineFieleds[2].split(b'/')[1].decode()      
                    elif line == b'' and not self.headerPassed: #and contentype contains multipart
                        if 'Content-Type' in self.headers.keys() and 'multipart' in self.headers['Content-Type']:
                            self.boundary = f"{self.headerFlags['Content-Type']['boundary']}".encode()
                            self.bodyLen += len(request[self.len + len(CRLF):])
                            print('hello')
                        else: self.headerPassed = True
                        
                        # if not 'multipart' in self.headers['Content-Type']:
                        #  headerPassed = True

                    
                    # elif 'Content-Type' in self.headerFlags.keys() and self.headerFlags['Content-Type'] != None:
                    #     if 'boundary' in self.headerFlags['Content-Type'].keys() and  line == self.headerFlags['Content-Type']['boundary'].encode():
                    #        print('tf?')
                    # elif i == 21:
                    #     # print('hello')
                    elif self.boundary != None and self.boundary in line:
                        self.boundaryPassed +=1
                    elif not self.headerPassed: # need to know how were in first part 
                        #headers
                        
                        #spaces dont always exist
                        # lineHeaderFields = line.split(b':')
                        # #adjust for two part header type with boundary
                        # rawKey = lineHeaderFields[0]
                        # rawValue = line[len(rawKey):] 
                        # value = rawValue.strip(b':').strip(b' ')
                        # key = rawKey.strip(b' ').decode()
                        # self.headers[key] = value.decode()
                        out = header2DictsB(line)
                        self.headers.update(out[0])
                        self.headerFlags.update(out[1])
                    elif self.headerPassed and not self.bodyParsed:# and not contentType contains multipart  
                        #body
                        if self.boundaryPassed == 0:
                            # self.body += line
                            # self.body += request[self.len:self.len+len(line)]
                            self.body += request[self.len:]
                            self.bodyParsed = True
                        else:
                            # self.body += request[self.len+len(CRLF):self.len+len(line)]
                            self.body += request[self.len+len(CRLF):]
                            # if b'PNG' in line:
                            #     self.body+=CRLF
                            self.bodyParsed = True
                    # elif self.headerFlags[]line == 'self.boundary' 
                    #elif headerPassed and contentType contains multipart
                        #parse line as second part
                    if self.headerPassed:
                        self.len+=len(line) 
                    else:
                        self.len += len(line) + len(CRLF)
                    i+=1
        print(b"MY PRINTED REQUEST BODY: " + self.body)
        if (self.path == '/profile-pic'):
            # print(self.body)
            print('END OF PARSING REQUEST')
            print(f"Giv Length:{self.headers['Content-Length']} | Parsed Length: {self.bodyLen}")
            if int(self.headers['Content-Length']) > self.bodyLen:
                print(f"REMAINING BYTES: {int(self.headers['Content-Length']) - self.bodyLen}")
                

