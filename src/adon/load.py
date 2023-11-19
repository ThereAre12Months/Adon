import struct

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
    "largedict"
]


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

    return val, ptr

def load(file:bytearray):
    if type(file) != bytearray:
        raise TypeError(f"Can only parse 'bytearray' not '{type(file).__name__}'!")
    
    obj = file.copy()

    val, _ = loadSomeValue(obj, 0)
    return val