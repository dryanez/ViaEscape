import json
import os
from shapely.geometry import shape, Point, mapping
from shapely.ops import nearest_points

class GeospatialEngine:
    def __init__(self):
        self.tsunami_zones = [] # List of shapely polygons
        self.evac_routes = []   # List of dicts
        self.meeting_points = [] # List of dicts
        self._load_data()

    def _load_data(self):
        """
        Loads GeoJSON files using standard json library.
        """
        base_path = os.path.dirname(__file__)
        routes_path = os.path.join(base_path, "vias_evacuacion.geojson")
        zones_path = os.path.join(base_path, "areas_evacuacion.geojson")
        points_path = os.path.join(base_path, "puntos_encuentro.geojson")
        
        # Load Evacuation Routes
        self.evac_routes = self._load_geojson_file(routes_path, "routes")
        
        # Load Tsunami Zones
        zones_data = self._load_geojson_file(zones_path, "zones")
        # Optimization: storing only geometry for zones might be faster for contain check
        self.tsunami_zones = [item['geometry'] for item in zones_data]

        # Load Meeting Points
        self.meeting_points = self._load_geojson_file(points_path, "meeting points")

    def _load_geojson_file(self, filepath, label):
        data_list = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"Loading {label} from {filepath}...")
                for feature in data['features']:
                    geom = shape(feature['geometry'])
                    data_list.append({
                        'geometry': geom,
                        'properties': feature['properties']
                    })
                print(f"Loaded {len(data_list)} {label}.")
            except Exception as e:
                print(f"Error loading {label}: {e}")
        else:
             print(f"WARNING: {label} not found at {filepath}.")
        return data_list

    def check_location(self, lat: float, lon: float):
        """
        Checks location against hazards and finds nearest route and meeting point.
        """
        user_point = Point(lon, lat)
        
        hazards = []
        
        # Check Tsunami Zones
        in_zone = False
        for zone in self.tsunami_zones:
            if zone.contains(user_point):
                hazards.append("Zona de Inundación por Tsunami")
                in_zone = True
                break 
        
        # Find nearest route
        nearest_route_info = self._find_nearest(user_point, self.evac_routes, "Route")
        
        # Find nearest meeting point
        nearest_point_info = self._find_nearest(user_point, self.meeting_points, "Meeting Point")

        is_safe = len(hazards) == 0    
        
        message = "Estás en una zona segura."
        if not is_safe:
            message = "¡ALERTA! Estás en una zona de riesgo de Tsunami."
        elif nearest_route_info and nearest_route_info['distance_meters'] < 500:
             message = "Estás cerca de una vía de evacuación."

        return {
            "safe": is_safe,
            "hazards": hazards,
            "nearest_route": nearest_route_info,
            "nearest_meeting_point": nearest_point_info,
            "message": message
        }

    def _find_nearest(self, user_point, features, type_label):
        if not features:
            return None
            
        min_dist = float('inf')
        nearest_feature = None
        
        for feature in features:
            dist = user_point.distance(feature['geometry'])
            if dist < min_dist:
                min_dist = dist
                nearest_feature = feature
        
        if nearest_feature:
            dist_meters = min_dist * 111139 
            
            # Find closest point on geometry (for lines/polygons) or just the point itself
            if nearest_feature['geometry'].geom_type == 'Point':
                closest_point = nearest_feature['geometry']
            else:
                closest_point = nearest_points(user_point, nearest_feature['geometry'])[1]
            
            dest_lat = closest_point.y
            dest_lon = closest_point.x

            # Handles different property names
            props = nearest_feature['properties']
            name = props.get('nom_com', props.get('nombre', props.get('Name', 'Unknown')))

            return {
                "distance_meters": round(dist_meters, 2),
                "name": f"{type_label} in {name}",
                "description": "Follow marked evacuation signs.",
                "geometry": mapping(nearest_feature['geometry']),
                "destination": {"lat": dest_lat, "lon": dest_lon}
            }
        return None


# Global instance
engine = GeospatialEngine()
