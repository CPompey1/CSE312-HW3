from util.Helpers import *
class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        self.body = b''
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.headerFlags = {}
        self.len= 0
        headerPassed = False
        CRLF = b'\r\n'
        bytesByLine = request.split(CRLF)
        numEmptyLines = 0

        if request.__len__()> 0:
            #debug line
            with open('requests','a') as file:
                    print(request,file=file)
            while bytesByLine[numEmptyLines] == b'':
                numEmptyLines+=1
            bytesByLine = bytesByLine[numEmptyLines:]
            for line in bytesByLine:
                if line == bytesByLine[0] and not headerPassed:
                    firstLineFieleds = line.split(b' ')
                    self.method = firstLineFieleds[0].strip(b' ').decode()
                    self.path = firstLineFieleds[1].strip(b' ').decode()
                    self.http_version = firstLineFieleds[2].split(b'/')[1].decode()      
                elif line == b'' and not headerPassed: #and contentype contains multipart
                    if 'Content-Type' in self.headers.keys() and not 'multipart' in self.headers['Content-Type']:
                        headerPassed = True 
                elif 'Content-Type' in self.headerFlags.keys() and 'boundary' in self.headerFlags['Content-Type'].keys() and line == self.headerFlags['Content-Type']['boundary'].encode():
                    print('tf?')
                elif not headerPassed: # need to know how were in first part 
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
                elif headerPassed:# and not contentType contains multipart  
                    #body
                    self.body += line
                #elif line == boundary pass
                #elif headerPassed and contentType contains multipart
                    #parse line as second part
                self.len += len(line) + len(CRLF)
        print(b"MY PRINTED STUFF:\n" + request)
        print(self.len)
        if (self.path == '/profile-pic'):
            # print(self.body)
            print('hi')
    