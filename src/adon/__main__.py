import json, argparse, os

from .adon import adonToJson, jsonToAdon
from . import __version__

def main():
    parser = argparse.ArgumentParser(
        prog='Adon',
        description='Converts JSON and Objects to a more compact format!',
        epilog='')
    
    parser.add_argument('-c', '--compile', nargs="+", default=[])      # option that takes a value
    parser.add_argument('-d', '--decompile', nargs="+", default=[])
    parser.add_argument('-v', '--version', action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"Version: {__version__}")

    if len(args.compile) == 1:
        jsonToAdon(args.compile[0], os.path.splitext(args.compile[0])+".adon")
    elif len(args.compile) == 2:
        jsonToAdon(args.compile[0], args.compile[1])

    if len(args.decompile) == 1:
        adonToJson(args.decompile[0], os.path.splitext(args.decompile[0])+".adon")
    elif len(args.decompile) == 2:
        adonToJson(args.decompile[0], args.decompile[1])

if __name__ == "__main__":
    main()