import dump, load
import json

product = {
    "price": 900.148,
    "weight": 5,
    "list": ["a", "b", "c"],
    "available": False,
    "type": "fruit"
}

jsonVer = json.dumps(product)
val = dump.dump(product)

print(f"JSON:  {len(jsonVer)}")
print(f"PyObj: {len(val)}")
print()
print(f"{round(len(jsonVer) / len(val), 2)}x more efficient")

val = load.load(val)
print(val)