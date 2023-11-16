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
        if len(splitHeader) <= 0:
            print('wtf')
        headerEntry[splitHeader[0].decode()] = splitHeader[1].decode().strip(' ')
        headerFlagEntry[splitHeader[0].decode()] = None
        return headerEntry,headerFlagEntry
    
# if __name__ == '__main__':
#     print(header2Dicts('sec-ch-ua: "Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"'))