# RPG_Engine
Small Python RPG Engine. Features will be added when I take the time.

## Map generation
To generate a map, use `utils/generate_map.py` file.
All data (maps and tilesets) needs to be stored into specific directories:
map files go into `/data/maps` and tilesets go into `/data/tiles`.

Follow these steps to generate a map file.
- Create a python file in `/utils` directory.
- Give it the same name as the map file you want to generate.
- Define all map data in a variable called `map_data`.
- Run the following command from `/utils` directory: ` python generate_map.py <python map file>`

For example, if you want to generate a file named `test.map`, create a file `test.py` and define
`map_data` variable then run `python generate_map.py test`.
