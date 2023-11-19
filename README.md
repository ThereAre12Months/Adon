# Adon
 Adon is a faster, more efficient alternative to JSON

### Why would you use Adon instead of JSON?
 - Adon files are on average 1.4x smaller then a JSON file.
 - In Adon a lot of the limitations of JSON are gone. (any type can be used as a key in a dictionary)

# Installation
**Using pip:**  

    python -m pip install adon  


# Usage
You can use Adon in the terminal and in a python script.

## Terminal
### Compiling JSON to Adon
You can compile JSON to Adon with the `adon -c` command, followed by the name of the JSON file and optionally the name of the Adon file.

```bash
adon -c someFile.json someFile.adon  
```
 \- compiles 'someFile.json' to 'someFile.adon'  

<br>

```bash
adon -c otherFile.json  
```
 \- compiles 'otherFile.json' to 'otherFile.adon'
***
### Decompiling Adon to JSON
You can decompile Adon to JSON using the `adon -d` command, followed by the Adon file and optionally the JSON file.  

```bash
adon -d someFile.adon someFile.json
```  
 \- decompiles 'someFile.adon' to 'someFile.json'  
<br>

```bash
adon -d otherFile.adon
```  
 \- decompiles 'otherFile.adon' to 'otherFile.json'

## Python script
### Compiling Python Object to Adon
The Adon module has a function `dump()` that can be used to convert a Python object to a bytearray with Adon formatting.

```python
import adon

product = {
    "name": "Magic Wand",
    "price": 109.5,
    "available": True,
    "category": "magic"
}

obj = adon.dump(product)
```

This Adon object can than be used on its own, or it can be written to a file:
```python
with open("fileName.adon", "wb") as f:
    f.write(obj)
```

**Note that currently only strings, integers, floats, booleans, lists and dictionaries are supported.**
***

### Decompiling Adon back to Python Object
The Adon module also contains a function to revert the Adon back to a Python object.

```python
import adon

fruits = [
    "banana",
    "apple",
    "mango"
]

# convert to Adon
obj = adon.dump(someFruit)

# convert to Python object
val = adon.load(obj)

print(val) 
# ['banana', 'apple', 'mango']
```