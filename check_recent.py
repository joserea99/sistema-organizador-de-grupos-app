import json
from datetime import datetime

with open('data/tableros.json', 'r') as f:
    data = json.load(f)

target_id = "51cf39a4-facf-4f75-b1a7-4037af150b69"

all_people = []

for tablero in data['tableros']:
    if tablero['id'] == target_id:
        for lista in tablero['listas']:
            for tarjeta in lista['tarjetas']:
                all_people.append(tarjeta)

# Sort by creation date (descending)
all_people.sort(key=lambda x: x.get('fecha_creacion', ''), reverse=True)

print(f"Most recent 5 people in tablero {target_id}:")
for p in all_people[:5]:
    print(f"- {p['nombre']} {p.get('apellido', '')}")
    print(f"  Created: {p.get('fecha_creacion')}")
    print(f"  Address: '{p.get('direccion')}'")
    print(f"  Coords: {p.get('latitud')}, {p.get('longitud')}")
    print("---")
