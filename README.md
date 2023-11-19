# PyObj
 PyObj is a faster, more efficient alternative to JSON

### Why would you use PyObj instead of JSON?
 - PyObj files are on average 1.4x smaller then a JSON file.
 - In PyObj a lot of the limitations of JSON are gone. (any type can be used as a key in a dictionary)

# Usage
You can use PyObj in the terminal and in a python script.

## Terminal
### Compiling JSON to PyObj
You can compile JSON to PyObj with the `pyo -c` command, followed by the name of the JSON file and optionally the name of the PyObj file.

`pyo -c someFile.json someFile.pyo`  
  -> compiles 'someFile.json' to 'someFile.pyo'  

`pyo -c otherFile.json`  
  -> compiles 'otherFile.json' to 'otherFile.pyo'
***
### Decompiling PyObj to JSON
You can decompile PyObj to JSON using the `pyo -d` command, followed by the PyObj file and optionally the JSON file.  

`pyo -d someFile.pyo someFile.json`  
  -> decompiles 'someFile.pyo' to 'someFile.json'

`pyo -d otherFile.pyo`  
  -> decompiles 'otherFile.pyo' to 'otherFile.json'

## Python script
### Compiling Python Object to PyObj
The PyObj module has a function `dump()` that can be used to convert a Python object to a bytearray with PyObj formatting.

```python
import pyobj

product = {
    "name": "Magic Wand",
    "price": 109.5,
    "available": True,
    "category": "magic
}

obj = pyobj.dump(product)
```

This PyObj object can than be used on its own, or it can be written to a file:
```python
with open("fileName.pyo", "wb") as f:
    f.write(obj)
```

**Note that currently only strings, integers, floats, booleans, lists and dictionaries are supported.**
***

### Decompiling PyObj back to Python Object
The PyObj module also contains a function to revert the PyObj back to a python object.

```python
import pyobj

fruits = [
    "banana",
    "apple",
    "mango"
]

# convert to PyObj
obj = pyobj.dump(someFruit)

# convert to Python object
val = pyobj.load(obj)

print(val) 
# ['banana', 'apple', 'mango']
```