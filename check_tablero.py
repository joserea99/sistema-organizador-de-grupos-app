import json

with open('data/tableros.json', 'r') as f:
    data = json.load(f)

target_id = "51cf39a4-facf-4f75-b1a7-4037af150b69"

for tablero in data['tableros']:
    if tablero['id'] == target_id:
        print(f"FOUND TABLERO: {tablero['nombre']} ({tablero['id']})")
        for lista in tablero['listas']:
            for tarjeta in lista['tarjetas']:
                lat = tarjeta.get('latitud')
                lng = tarjeta.get('longitud')
                address = tarjeta.get('direccion')
                
                print(f"  - {tarjeta['nombre']} {tarjeta.get('apellido', '')}: '{address}' (Lat: {lat}, Lng: {lng})")
