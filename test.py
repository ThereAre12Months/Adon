import dump, load
import json

product = {
    "price": 90000000,
    "isValid": False,
    "type": "fruit"
}
jsonVer = json.dumps(product)
val = dump.dump(product)

print(f"JSON:  {len(jsonVer)}")
print(f"PyObj: {len(val)}")
print()
print(f"{round(len(jsonVer) / len(val), 2)}x more efficient")
print()
print(jsonVer)
val = load.load(val)
