import importlib
import pickle
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <python map file>")
    sys.exit(-1)

module = importlib.import_module("utils." + sys.argv[1])

if not hasattr(module, "map_data"):
    print("No 'map_data' variable defined in module!")
    sys.exit(-2)

with open("../data/maps/test.map", "wb") as f:
    pickle.dump(module.map_data, f)
