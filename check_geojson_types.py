
import json
from collections import Counter

try:
    with open('api/vias_evacuacion.geojson', 'r') as f:
        data = json.load(f)
        
    types = Counter()
    for feature in data['features']:
        geom_type = feature['geometry']['type']
        types[geom_type] += 1
        
    print("Geometry Types Found:")
    for type_name, count in types.items():
        print(f"{type_name}: {count}")
        
except Exception as e:
    print(f"Error: {e}")
