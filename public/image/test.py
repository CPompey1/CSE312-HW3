#Counts the number of CRLFS in the given file
CRLF = b'\r\n'
file  = open('cat.jpg','rb') 
out = file.read()
file.close()
file = open('test_Screenshot (2).png','rb')
out1 = file.read()
foundIndex = 0
noneFound = False
numFound = 0
while (foundIndex < len(out) and numFound < len(out) and not noneFound):
    index = out[foundIndex:foundIndex+20].find(CRLF)
    
    print(index)
    if index < 0:        
        noneFound = True
    else:
        foundIndex += index + 1
        numFound +=1
print(f'Num CRLFs Found: {numFound}, length of file: {len(out)}')
