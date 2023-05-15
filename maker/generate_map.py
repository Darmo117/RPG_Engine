import importlib
import sys
import gzip

from engine import io

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} <python map file>')
    sys.exit(-1)

name = sys.argv[1]
module = importlib.import_module(name)

if not hasattr(module, 'map_data'):
    print('No "map_data" variable defined in module!')
    sys.exit(-2)

with gzip.open(f'../run/data/maps/{name}.map', 'wb') as f:
    buffer = io.ByteBuffer()
    data = module.map_data
    buffer.write_int(1, signed=False)
    for v in data['size']:
        buffer.write_short(v, signed=False)
    for v in data['bg_color']:
        buffer.write_byte(v, signed=False)
    buffer.write_byte(data['entity_layer'], signed=False)
    layers_nb = len(data['tiles'])
    buffer.write_byte(layers_nb, signed=False)
    for layer in data['tiles']:
        for row in layer:
            for tileset_id, tile_id in row:
                buffer.write_short(tileset_id, signed=False)
                buffer.write_short(tile_id, signed=False)
    for row in data['interactions']:
        for interaction in row:
            interaction.write_to_buffer(buffer)
    f.write(buffer.bytes)
    print('Map file generated')
