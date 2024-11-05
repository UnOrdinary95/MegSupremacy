import os
import json

maps_json_path = os.path.join("..","data","maps.json")
brawlers_json_path = os.path.join("..", "data", "list_brawlers.json")

with open(maps_json_path, "r") as file:
    maps_json = json.load(file)

with open(brawlers_json_path, "r") as file:
    brawlers_json = json.load(file)