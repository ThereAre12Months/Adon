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

def getType(val):
    return DATATYPES[val >> 4]

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
        type_ = getType(obj[ptr])
        match type_:
            case "string":
                val, ptr = loadString(obj, ptr)
            case "uInt":
                val, ptr = loadInt(obj, ptr)

            case "varia":
                val, ptr = loadVaria(obj, ptr)

            case _:
                raise NotImplementedError(type_, ptr)
        
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

def loadVaria(obj, pointer):
    ptr = pointer
    val = obj[ptr] - ((obj[ptr] >> 4) << 4)

    val = [False, True, None][val]

    return val, ptr+1

def load(file:bytearray):
    if type(file) != bytearray:
        raise TypeError(f"Can only parse 'bytearray' not '{type(file).__name__}'!")
    
    obj = file.copy()

    pointer = 0
    vals = []
    while pointer < len(obj):
        match getType(obj[pointer]):
            case "string":
                val, pointer = loadString(obj, pointer)

            case "uInt":
                val, pointer = loadInt(obj, pointer)

            case "varia":
                val, pointer = loadVaria(obj, pointer)

            case "smalldict":
                val, pointer = loadDict(obj, pointer, size="small")
            
            case "mediumdict":
                val, pointer = loadDict(obj, pointer, size="medium")

            case "largedict":
                val, pointer = loadDict(obj, pointer, size="large")

        vals.append(val)

    if len(vals) == 1:
        return vals[0]
    else:
        return vals