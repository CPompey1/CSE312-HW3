import json
import bcrypt
from util.Frame import Frame
from util.Global import DB


def header2Dicts (header: str):
    headerEntry = {}
    headerFlagEntry = {}
    
    if ';' in header:
        splitHeader = header.split(':')
        splitFields = splitHeader[1].split(';')
        i = 0
        for ele in splitFields:
            if i == 0:
                headerEntry[splitHeader[0]] = ele
                headerFlagEntry[splitHeader[0]] = {}
            else:
                splitField = ele.split('=')
                if len(splitField) > 1:
                    headerFlagEntry[splitHeader[0]][splitField[0]] = splitField[1]
            i+=1
        return headerEntry,headerFlagEntry
    else:
        splitHeader = header.split(':')
        headerEntry[splitHeader[0]] = splitHeader[1]
        headerFlagEntry[splitHeader[0]] = None
        return headerEntry,headerFlagEntry

def header2DictsB (header: bytes):
    headerEntry = {}
    headerFlagEntry = {}
    
    if b';' in header:
        splitHeader = header.split(b':')
        splitFields = splitHeader[1].split(b';')
        i = 0
        for ele in splitFields:
            if i == 0:
                headerEntry[splitHeader[0].decode().strip(' ')] = ele.decode().strip(' ')
                headerFlagEntry[splitHeader[0].decode().strip(' ')] = {}
            else:
                splitField = ele.split(b'=')
                if len(splitField) > 1:
                    headerFlagEntry[splitHeader[0].decode().strip(' ')][splitField[0].decode().strip(' ')] = splitField[1].decode().strip(' ')
            i+=1
        return headerEntry,headerFlagEntry
    else:
        splitHeader = header.split(b':')
        if len(splitHeader) <= 1:
            print('wtf')
        else:
            headerEntry[splitHeader[0].decode()] = splitHeader[1].decode().strip(' ')
            headerFlagEntry[splitHeader[0].decode()] = None
        return headerEntry,headerFlagEntry

def getCookies(request):
    if 'Cookie' in request.headers: return request.headers['Cookie']
    else: return None
def authenticate(request):
    cookies = getCookies(request)
    if cookies == None or type(cookies) == type(dict()):
        return None
    token = cookies.split("=")[1]
    possibleUser = DB.findOne_asList(collection='tokens',keysToSearch={'token':bcrypt.hashpw(token.encode(),DB.TOKENSALT)})
    if len(possibleUser) == 0:
        return None
    try:
        user = possibleUser[0]['username']
    except TypeError:
        return None
    return user,token    

def replaceDangeChar(input):
    return input.replace('&','&amp').replace('<','&lt').replace('>','&gt')

def bytes_to_binary_string(the_byte):
    as_binary = str(bin(the_byte))[2:]
    for _ in range(len(as_binary),8):
        as_binary = '0' + as_binary
    return as_binary

def bytes_to_binary_string_le(the_byte):
    as_binary = str(bin(the_byte))[2:]
    for _ in range(len(as_binary),8):
        as_binary = '0' + as_binary
    out = ''
    for i in range(len(as_binary)):
        out += as_binary[len(as_binary)-1 - i]
    return out

def getDirOfFile(path):
    splitPath = path.split('/')
    splitPath.remove(splitPath[len(splitPath)-1])
    out = ''
    for ele,i in zip(splitPath,range(len(splitPath))):
        out +=ele
        
        if i != len(splitPath):
            out += '/'
    return out

def certifyPath(path):
    foundIdx = path.find("/public")
    if foundIdx <0:
        return ''
    afterPublicImg = path[foundIdx + len("/public"):]
    beforePublicImg = path[:foundIdx + len("/public")]
    path = afterPublicImg.replace('../','')
    return beforePublicImg + path
def findDifIdx(real,created):
    for i in range(len(real)):
        try:
            if real[i] != created[i]:
                if i != 0:
                    print(f"DIFF AT INDEX: {i}")
                    print(f"GIVEN: {created[i-57%i+1:i+57%i+1]}")
                    print(f"EXPECTED: {real[i-57%i+1:i+57%i+1]}")
                    return i
        except IndexError:
            print(f"ERROR: Lengths dont match. Given: {len(created)} | Expected: {len(real)}")
# if __name__ == '__main__':
#     print(header2Dicts('Cache-Control: max-age=0'))