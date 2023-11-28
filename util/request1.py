from util.Helpers import *
class Request:
    
    def __init__(self,request,exiBuffer=None) -> None:
        CRLF = b'\r\n'
        if len(request) > 0:
            if exiBuffer != None:
                self.extendBuffer(request,exiBuffer)
            else: self.initBuffer(request)
        
    def initBuffer(self,request):
        CRLF = b'\r\n'
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


        #http header line
        i = 0
        bytesByLine = request.split(CRLF)
        for line in bytesByLine:
            if line == bytesByLine[0] and not self.headerPassed:
                firstLineFieleds = line.split(b' ')
                self.method = firstLineFieleds[0].strip(b' ').decode()
                self.path = firstLineFieleds[1].strip(b' ').decode()
                self.http_version = firstLineFieleds[2].split(b'/')[1].decode()      
            elif line == b'' and not self.headerPassed: #and contentype contains multipart
                if 'Content-Type' in self.headers.keys() and 'multipart' in self.headers['Content-Type']:
                    self.boundary = f"{self.headerFlags['Content-Type']['boundary']}".encode()
                    print('hello')
                else: 
                    self.headerPassed = True
                    
            elif self.boundary != None and self.boundary in line:
                self.boundaryPassed +=1
            elif not self.headerPassed: # need to know how were in first part 
                #headers
                out = header2DictsB(line)
                self.headers.update(out[0])
                self.headerFlags.update(out[1])
            elif self.headerPassed and not self.bodyParsed:# and not contentType contains multipart  
                #body
                if self.boundaryPassed == 0:
                    # self.body += line
                    pass
                else:
                    self.body += request[self.len:len(request)-1]
                    if b'PNG' in line:
                        self.body+=CRLF
                    self.bodyParsed = True
            self.len += len(line) + len(CRLF)
            i+=1

        # if self.headerPassed:
        #     self.body += request[self.len:len(request)-1]

        #     self.len += len(request[self.len:len(request)-1])
             
        

    def extendBuffer(self,request,exiBuffer):
        CRLF = b'\r\n'
        i = 0
        runningLen = 0
        bytesByLine = request.split(CRLF)

        #gonna assume only headers and body is left
        for line in bytesByLine:
            if exiBuffer.boundary != None and exiBuffer.boundary in line:
                exiBuffer.boundaryPassed +=1
            elif line == b'' and not exiBuffer.headerPassed: #and contentype contains multipart
                    if 'Content-Type' in exiBuffer.headers.keys() and 'multipart' in exiBuffer.headers['Content-Type']:
                        exiBuffer.boundary = f"{exiBuffer.headerFlags['Content-Type']['boundary']}".encode()
                        print('hello')
                    else: 
                        exiBuffer.headerPassed = True
                    
            elif not exiBuffer.headerPassed: # need to know how were in first part 
                    #headers
                    out = header2DictsB(line)
                    exiBuffer.headers.update(out[0])
                    exiBuffer.headerFlags.update(out[1])
            #line is raw bytes
            else:
                exiBuffer.body += request[runningLen:runningLen + len(line)]
                if b'PNG' in line: exiBuffer.body+=CRLF
            i+=1
            runningLen += len(line) + len(CRLF)
            exiBuffer.len += len(line) + len(CRLF)
        


        for classAttr in exiBuffer.__dict__.keys():
            self.__dict__[classAttr] = exiBuffer.__dict__[classAttr]
