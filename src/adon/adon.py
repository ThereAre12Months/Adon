import struct, math, json

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
BYTES     = 12

# map of values in 'VARIA'
FALSE = 0
TRUE  = 1
NONE  = 2

# REVERSE DATATYPE MAPPING
DATATYPES = [
    "Template",
    "uInt",
    "sInt",
    "float",
    "string",
    "varia",
    "smalllist",
    "mediumlist",
    "largelist",
    "smalldict",
    "mediumdict",
    "largedict",
    "bytes"
]

# Python Object to Adon
def getWeirdEndian(num):
    big    = num >> 16
    medium = (num - (big << 16)) >> 8
    small  = num - (big << 16) - (medium << 8)
    
    return big, medium, small

def splitInChunks(val:str, size:int=8):
    copy = val 

    chunks = []

    while len(copy) > size:
        chunks.append(copy[-size:])
        copy = copy[:-size]

    chunks.append(copy)
    chunks.reverse()

    return chunks

def getWeirdEndianBig(num):
    return list(map(lambda val: int(val, base=2), splitInChunks(bin(num)[2:], size=8)))

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

def addBytearray(arr:bytearray, ba:bytearray):
    len_ = len(ba)
    splitted = getWeirdEndianBig(len_)

    while len(splitted) < 8:
        splitted.insert(0, 0)

    if len(splitted) > 8:
        raise ValueError("Files can be no bigger than 1 Exabyte!")

    arr.append((BYTES << 4) + splitted[0])
    arr.extend(splitted[1:])

    arr.extend(ba)

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
    elif type(object) == bytearray or type(object) == bytes:
        addBytearray(arr, bytearray(object))
    else:
        raise NotImplementedError(f"Can't add item of type '{type(object).__name__}'")

def dump(object:any):
    arr = bytearray()
    addSomeVal(arr, object)

    return arr

# Adon to Python Object

def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]

def getType(val):
    return DATATYPES[val >> 4]

def loadList(obj:bytearray, pointer:int, size:str="small"):
    amount = 0
    ptr = pointer
    if size == "small":
        amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
    elif size == "medium":
        amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
        ptr += 1
        amount = (amount << 8) + obj[ptr]
    elif size == "large":
        amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
        ptr += 1
        amount = (amount << 8) + obj[ptr]
        ptr += 1
        amount = (amount << 8) + obj[ptr]

    ptr += 1

    vals = []
    for _ in range(amount):
        val, ptr = loadSomeValue(obj, ptr)
        vals.append(val)

    return vals, ptr

def loadDict(obj, pointer:int, size:str="small"):
    amount = 0
    ptr = pointer
    if size == "small":
        amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
    elif size == "medium":
        amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
        ptr += 1
        amount = (amount << 8) + obj[ptr]
    elif size == "large":
        amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
        ptr += 1
        amount = (amount << 8) + obj[ptr]
        ptr += 1
        amount = (amount << 8) + obj[ptr]

    ptr += 1

    vals = []
    for _ in range(amount * 2):
        val, ptr = loadSomeValue(obj, ptr)
        vals.append(val)

    it = iter(vals)
    return dict(zip(it, it)), ptr

def loadString(obj:bytearray, pointer):
    ptr = pointer

    length = obj[ptr] - ((obj[ptr] >> 4) << 4)
    ptr += 1
    length = (length << 8) + obj[ptr]
    ptr += 1

    val = obj[ptr:ptr+length].decode("utf-8")

    return val, ptr+length

def loadInt(obj, pointer):
    ptr = pointer
    length = obj[ptr] - ((obj[ptr] >> 4) << 4)
    ptr += 1

    selected = obj[ptr:ptr+length]
    val = 0
    for i in selected:
        val = val << 8
        val += i

    return val, ptr+length

def loadSInt(obj, pointer):
    ptr = pointer
    length = obj[ptr] - ((obj[ptr] >> 4) << 4)
    ptr += 1

    selected = obj[ptr:ptr+length]
    val = ""
    for i in selected:
        val += format(i, "08b")

    sign = val[0]
    val  = val[1:]

    if sign == "1":
        val = int(val, 2) - 2**len(val)
    else:
        val = int(val, 2)

    return val, ptr+length

def loadFloat(obj, pointer):
    ptr = pointer
    length = obj[ptr] - ((obj[ptr] >> 4) << 4)
    ptr += 1

    selected = obj[ptr:ptr+length]
    val = ""
    for i in selected:
        val += format(i, "08b")
    val = bin_to_float(val)

    return val, ptr+length

def loadVaria(obj, pointer):
    ptr = pointer
    val = obj[ptr] - ((obj[ptr] >> 4) << 4)

    val = [False, True, None][val]

    return val, ptr+1

def loadBytes(obj, pointer):
    ptr = pointer

    amount = obj[ptr] - ((obj[ptr] >> 4) << 4)
    ptr += 1
    for i in range(7):
        amount = (amount << 8) + obj[ptr]
        ptr += 1
    
    return obj[ptr:ptr+amount], ptr+amount

def loadSomeValue(obj:bytearray, pointer):
    ptr = pointer
    type_ = getType(obj[ptr])
    match type_:
        case "string":
            val, ptr = loadString(obj, ptr)
        case "uInt":
            val, ptr = loadInt(obj, ptr)
        case "sInt":
            val, ptr = loadSInt(obj, ptr)
        case "float":
            val, ptr = loadFloat(obj, ptr)
        case "varia":
            val, ptr = loadVaria(obj, pointer)
        case "smalldict":
            val, ptr = loadDict(obj, ptr, size="small")
        case "mediumdict":
            val, ptr = loadDict(obj, ptr, size="medium")
        case "largedict":
            val, ptr = loadDict(obj, ptr, size="large")
        case "smalllist":
            val, ptr = loadList(obj, ptr, size="small")
        case "mediumlist":
            val, ptr = loadList(obj, ptr, size="medium")
        case "largelist":
            val, ptr = loadList(obj, ptr, size="large")
        case "bytes":
            val, ptr = loadBytes(obj, ptr)

    return val, ptr

def load(file:bytearray|bytes):
    if not (type(file) == bytearray or type(file) == bytes):
        raise TypeError(f"Can only parse 'bytearray' and 'bytes' not '{type(file).__name__}'!")
    
    obj = bytearray(file)

    val, _ = loadSomeValue(obj, 0)
    return val

# other funcs
def jsonToAdon(jsonPath, newPath):
    with open(jsonPath, "r") as f:
        dict_ = json.load(f)

    with open(newPath, "wb") as f:
        f.write(dump(dict_))

def adonToJson(oldPath, newPath):
    with open(oldPath, "rb") as f:
        dict_ = load(bytearray(f.read()))

    with open(newPath, "w") as f:
        f.write(json.dumps(dict_, indent=2))