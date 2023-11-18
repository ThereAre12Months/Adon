# DATATYPE MAPPING
TEMPLATE  = 0
UINT      = 1
SINT      = 2
FLOAT     = 3
STRING    = 4
VARIA     = 5
SMALLLIST = 6
MEDLIST   = 7
LARGELIST = 8
SMALLDICT = 9
MEDDICT   = 10
LARGEDICT = 11

# map of values in 'VARIA'
FALSE = 0
TRUE  = 1
NONE  = 3

def getWeirdEndian(num):
    big    = num >> 16
    medium = (num - (big << 16)) >> 8
    small  = num - (big << 16) - (medium << 8)
    
    return big, medium, small

def splitInChunks(val:str, size:int):
    copy = val 

    chunks = []

    while len(copy) > size:
        chunks.append(copy[-size:])
        copy = copy[:-size]

    chunks.append(copy)
    chunks.reverse()

    return chunks

def addVaria(arr, val):
    if type(val) == bool:
        v = int(val)
    else:
        v = 3
        
    arr.append((VARIA << 4) + v)

def addString(arr, val):
    stringArr = bytearray(val, "utf-8")

    len_ = len(stringArr)
    _, medium, small = getWeirdEndian(len_)

    if len_ > 4095:
        raise ValueError("Maximum string length of 4095")
    
    arr.append((STRING << 4) + medium)
    arr.append(small)

    arr += stringArr

def addInt(arr:bytearray, val):
    binVal = bin(val)[2:]
    chunks = splitInChunks(binVal, 8)
    len_ = len(chunks)

    if len_ > 15:
        raise ValueError("Maximum int size exceeded")
    
    arr.append((UINT << 4) + len_)

    for chunk in chunks:
        arr.append(int(chunk, 2))

def addDict(arr, dict_):
    
    len_ = len(tuple(dict_.keys()))
    big, medium, small = getWeirdEndian(len_)

    if len_ < 16:
        arr.append((SMALLDICT << 4) + small)
    elif len_ < 4096:
        arr.append((MEDDICT << 4) + medium)
        arr.append(small)
    elif len_ < 1048576:
        arr.append((LARGEDICT << 4) + big)
        arr.append(medium)
        arr.append(small)
    else:
        raise ValueError(f"Too many dictionary entries!")

    for key in dict_.keys():
        if type(key) == str:
            addString(arr, key)
        elif type(key) == int:
            addInt(arr, key)
        elif type(key) == bool:
            addVaria(arr, key)
        else:
            raise TypeError(f"Can't use type '{type(key).__name__}' as key in dictionary!")
        
        val = dict_[key]
        if type(val) == str:
            addString(arr, val)
        elif type(val) == int:
            addInt(arr, val)
        elif type(val) == bool:
            addVaria(arr, val)

def dump(object:dict):
    if not type(object) == dict:
        raise NotImplementedError("PyObj.dump() only works on dictionaries")
    
    arr = bytearray()
    addDict(arr, object)

    return arr
    
    
