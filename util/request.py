class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        self.body = b''
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        headerPassed = False
        CRLF = b'\r\n'
        bytesByLine = request.split(CRLF)
        numEmptyLines = 0

        if request.__len__()> 0:
            #debug line
            with open('requests','a') as file:
                    print(request.decode(),file=file)
            while bytesByLine[numEmptyLines] == b'':
                numEmptyLines+=1
            bytesByLine = bytesByLine[numEmptyLines:]
            for line in bytesByLine:
                if line == bytesByLine[0] and not headerPassed:
                    firstLineFieleds = line.split(b' ')
                    self.method = firstLineFieleds[0].strip(b' ').decode()
                    self.path = firstLineFieleds[1].strip(b' ').decode()
                    self.http_version = firstLineFieleds[2].split(b'/')[1].decode()      
                elif line == bytesByLine[len(bytesByLine) -1] and not headerPassed:
                    pass
                elif line == b'' and not headerPassed:
                    headerPassed = True 
                elif not headerPassed:
                    #headers
                    #spaces dont always exist
                    lineHeaderFields = line.split(b':')
                    rawKey = lineHeaderFields[0]
                    rawValue = line[len(rawKey):] 
                    value = rawValue.strip(b':').strip(b' ')
                    key = rawKey.strip(b' ').decode()
                    self.headers[key] = value.decode()
                elif headerPassed:  
                    #body
                    self.body += line
        
        if (self.path == '/profile-pic'):
            print(self.body)