import json, argparse, os

from .dump import dump
from .load import load

def main():
    parser = argparse.ArgumentParser(
        prog='Adon',
        description='Converts JSON and Objects to a more compact format!',
        epilog='')
    
    parser.add_argument('-c', '--compile', nargs="+", default=[])      # option that takes a value
    parser.add_argument('-d', '--decompile', nargs="+", default=[])

    args = parser.parse_args()

    if len(args.compile) == 1:
        jsonToAdon(args.compile[0], os.path.splitext(args.compile[0])+".adon")
    elif len(args.compile) == 2:
        jsonToAdon(args.compile[0], args.compile[1])

    if len(args.decompile) == 1:
        AdonToJson(args.decompile[0], os.path.splitext(args.decompile[0])+".adon")
    elif len(args.decompile) == 2:
        AdonToJson(args.decompile[0], args.decompile[1])
    

def jsonToAdon(jsonPath, newPath):
    with open(jsonPath, "r") as f:
        dict_ = json.load(f)

    with open(newPath, "wb") as f:
        f.write(dump(dict_))

def AdonToJson(oldPath, newPath):
    with open(oldPath, "rb") as f:
        dict_ = load(bytearray(f.read()))

    with open(newPath, "w") as f:
        f.write(json.dumps(dict_, indent=2))

if __name__ == "__main__":
    main()