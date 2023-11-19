import struct, math

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
NONE  = 2

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
        v = 2

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

def addUInt(arr:bytearray, val):
    binVal = bin(val)[2:]
    chunks = splitInChunks(binVal, 8)
    len_ = len(chunks)

    if len_ > 15:
        raise ValueError("Maximum int size exceeded")
    
    arr.append((UINT << 4) + len_)

    for chunk in chunks:
        arr.append(int(chunk, 2))

def makeNegative(bitstring:str):
    bits = bitstring
    bits = bits.zfill(math.ceil(len(bits) / 8) * 8)

    # invert
    temp = ""
    for bit in bits:
        if bit == "0":
            temp += "1"
        else:
            temp += "0"

    bits = temp

    intVal = int(bits, 2)+1

    bits = bin(intVal)[2:]
    bits = bits.zfill(math.ceil(len(bits)/8)*8)

    return bits

def addSInt(arr:bytearray, val:int):
    binVal = bin(abs(val))[2:]

    if val < 0:
        binVal = makeNegative(binVal)

    chunks = splitInChunks(binVal, 8)

    arr.append((SINT << 4) + len(chunks))

    for chunk in chunks:
        arr.append(int(chunk, 2))

def float_to_bin(num):
    return format(struct.unpack('!I', struct.pack('!f', num))[0], '032b')

def addFloat(arr:bytearray, val):
    binVal = float_to_bin(val)
    chunks = splitInChunks(binVal, 8)
    len_ = len(chunks)

    arr.append((FLOAT << 4) + len_)
    for chunk in chunks:
        arr.append(int(chunk, 2))
    

def addList(arr:bytearray, val:list):
    len_ = len(val)
    big, medium, small = getWeirdEndian(len_)

    if len_ < 16:
        arr.append((SMALLLIST << 4) + small)
    elif len_ < 4096:
        arr.append((MEDLIST << 4) + medium)
        arr.append(small)
    elif len_ < 1048576:
        arr.append((LARGELIST << 4) + big)
        arr.append(medium)
        arr.append(small)
    
    for i in val:
        addSomeVal(arr, i)

def addDict(arr:bytearray, dict_:dict):
    
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
        addSomeVal(arr, key)
        
        val = dict_[key]
        addSomeVal(arr, val)

def addSomeVal(arr, object):
    if type(object) == str:
        addString(arr, object)
    elif type(object) == int:
        if object >= 0:
            addUInt(arr, object)
        else:
            addSInt(arr, object)
    elif type(object) == float:
        addFloat(arr, object)
    elif type(object) == bool or object == None:
        addVaria(arr, object)
    elif type(object) == dict:
        addDict(arr, object)
    elif type(object) == list or type(object) == tuple:
        addList(arr, object)
    else:
        raise NotImplementedError(f"Can't add item of type '{type(object).__name__}'")

def dump(object:any):
    arr = bytearray()
    addSomeVal(arr, object)

    return arr
    
    
