import os
import fiona
from shapely.geometry import shape, Point, mapping
from shapely.ops import nearest_points

class GeospatialEngine:
    def __init__(self):
        self.tsunami_zones = [] # List of shapely geometries
        self.evac_routes = []   # List of dicts with 'geometry' and 'properties'
        self._load_data()

    def _load_data(self):
        """
        Loads shapefiles using fiona (lightweight) instead of geopandas.
        """
        data_path = ".tmp/data"
        user_data_path = "Vías_de_Evacuación_Tsunami/vias_evacuacion.shp"
        
        # Load Evacuation Routes (User Provided)
        if os.path.exists(user_data_path):
            try:
                with fiona.open(user_data_path) as source:
                    # Check CRS (heuristic, fiona returns proj4 string or dict)
                    # We assume it's roughly correct or we might need handling if it't not EPSG:4326
                    # For this MVP we trust source or simple user files.
                    print(f"Loading routes from {user_data_path}...")
                    for feature in source:
                        geom = shape(feature['geometry'])
                        self.evac_routes.append({
                            'geometry': geom,
                            'properties': feature['properties']
                        })
                print(f"Loaded {len(self.evac_routes)} evacuation routes.")
            except Exception as e:
                print(f"Error loading routes: {e}")
        else:
             print(f"WARNING: Evacuation routes not found at {user_data_path}. Using empty mock.")

        # Placeholder for Tsunami Zones (Pending)
        tsunami_path = os.path.join(data_path, "tsunami", "evacuation_area.shp")
        if os.path.exists(tsunami_path):
            try:
                 with fiona.open(tsunami_path) as source:
                    for feature in source:
                        self.tsunami_zones.append(shape(feature['geometry']))
            except Exception as e:
                print(f"Error loading tsunami zones: {e}")

    def check_location(self, lat: float, lon: float):
        """
        Checks location against hazards and finds nearest route.
        """
        user_point = Point(lon, lat)
        
        hazards = []
        nearest_route_info = None

        # Check Tsunami Zones
        for zone in self.tsunami_zones:
            if zone.contains(user_point):
                hazards.append("Tsunami Evacuation Zone")
                break # Found one, that's enough for warning
        
        # Find nearest route
        if self.evac_routes:
            min_dist = float('inf')
            nearest_feature = None
            
            # Linear search (slow for massive data, but okay for MVP with <3000 routes)
            # A spatial index (rtree) would be better but requires more dependencies
            for feature in self.evac_routes:
                dist = user_point.distance(feature['geometry'])
                if dist < min_dist:
                    min_dist = dist
                    nearest_feature = feature
            
            if nearest_feature:
                # Approximate conversion deg to meters (at these latitudes ~111km/deg)
                dist_meters = min_dist * 111139 
                
                # Find the point on the route closest to the user
                closest_point_on_route = nearest_points(user_point, nearest_feature['geometry'])[1]
                
                dest_lat = closest_point_on_route.y
                dest_lon = closest_point_on_route.x

                nearest_route_info = {
                    "distance_meters": round(dist_meters, 2),
                    "name": f"Route in {nearest_feature['properties'].get('nom_com', 'Unknown')}",
                    "description": "Follow marked evacuation signs.",
                    "geometry": mapping(nearest_feature['geometry']),
                    "destination": {"lat": dest_lat, "lon": dest_lon}
                }

        is_safe = len(hazards) == 0    
        
        return {
            "safe": is_safe,
            "hazards": hazards,
            "nearest_route": nearest_route_info,
            "message": "You are near evacuation routes!" if nearest_route_info else "No nearby routes found."
        }


# Global instance
engine = GeospatialEngine()
