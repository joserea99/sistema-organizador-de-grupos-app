import json

with open('data/tableros.json', 'r') as f:
    data = json.load(f)

count = 0
for tablero in data['tableros']:
    print(f"Tablero: {tablero['nombre']}")
    for lista in tablero['listas']:
        for tarjeta in lista['tarjetas']:
            if tarjeta.get('direccion') and (not tarjeta.get('latitud') or tarjeta.get('latitud') == 0):
                print(f"  - {tarjeta['nombre']} {tarjeta.get('apellido', '')}: '{tarjeta['direccion']}' (Lat: {tarjeta.get('latitud')})")
                count += 1

print(f"Total uncoded: {count}")
