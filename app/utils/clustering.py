import math
import googlemaps
from typing import List, Dict, Any, Tuple
from app.models import Tarjeta

class ClusteringManager:
    def __init__(self, api_key: str = None):
        if api_key:
            self.gmaps = googlemaps.Client(key=api_key)
        else:
            self.gmaps = None

    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Geocodificar una dirección a coordenadas (lat, lng)"""
        if not self.gmaps:
            print("Error: Google Maps Client not initialized (no API key)")
            return None, None
            
        try:
            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return location['lat'], location['lng']
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
        return None, None

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcular distancia en millas entre dos puntos (Haversine)"""
        R = 3958.8  # Radio de la Tierra en millas
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def create_clusters(self, personas: List[Dict], max_distance_miles: float, min_size: int, max_size: int) -> List[Dict]:
        """
        Agrupar personas basadas en proximidad geográfica.
        Algoritmo Greedy simple:
        1. Tomar una persona no asignada como 'semilla'.
        2. Encontrar todos los vecinos dentro del radio.
        3. Si el grupo cumple min_size, crearlo. Si excede max_size, dividirlo.
        """
        unassigned = [p for p in personas if p.get('latitud') and p.get('longitud')]
        clusters = []
        
        while unassigned:
            seed = unassigned.pop(0)
            cluster = [seed]
            
            # Encontrar vecinos
            neighbors = []
            for p in unassigned:
                dist = self.calculate_distance(seed['latitud'], seed['longitud'], p['latitud'], p['longitud'])
                if dist <= max_distance_miles:
                    neighbors.append((dist, p))
            
            # Ordenar por distancia
            neighbors.sort(key=lambda x: x[0])
            
            # Agregar vecinos al cluster hasta max_size
            for _, p in neighbors:
                if len(cluster) < max_size:
                    cluster.append(p)
                    unassigned.remove(p)
            
            # Verificar tamaño mínimo
            if len(cluster) >= min_size:
                clusters.append({
                    'center': {'lat': seed['latitud'], 'lng': seed['longitud']},
                    'members': cluster,
                    'count': len(cluster)
                })
            else:
                # Si no cumple el mínimo, devolver a unassigned (o manejar como outliers)
                # Por simplicidad en esta v1, los dejamos como un cluster pequeño o outliers
                # Opción: Intentar fusionar con el cluster más cercano existente
                clusters.append({
                    'center': {'lat': seed['latitud'], 'lng': seed['longitud']},
                    'members': cluster,
                    'count': len(cluster),
                    'is_outlier': True
                })
                
        return clusters
