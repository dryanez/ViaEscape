import geopandas as gpd
from shapely.geometry import Point
import os

class GeospatialEngine:
    def __init__(self):
        self.tsunami_zones = None
        self.meeting_points = None
        self._load_data()

    def _load_data(self):
        """
        Loads shapefiles from .tmp/data/ and local user folders.
        """
        data_path = ".tmp/data"
        user_data_path = "Vías_de_Evacuación_Tsunami/vias_evacuacion.shp"
        
        # Load Evacuation Routes (User Provided)
        if os.path.exists(user_data_path):
            try:
                self.evac_routes = gpd.read_file(user_data_path)
                if self.evac_routes.crs != "EPSG:4326":
                    self.evac_routes = self.evac_routes.to_crs("EPSG:4326")
                print(f"Loaded {len(self.evac_routes)} evacuation routes.")
            except Exception as e:
                print(f"Error loading routes: {e}")
                self.evac_routes = gpd.GeoDataFrame(geometry=[])
        else:
             print(f"WARNING: Evacuation routes not found at {user_data_path}. Using empty mock.")
             self.evac_routes = gpd.GeoDataFrame(geometry=[])

        # Placeholder for Tsunami Zones (Pending)
        tsunami_path = os.path.join(data_path, "tsunami", "evacuation_area.shp")
        if os.path.exists(tsunami_path):
            self.tsunami_zones = gpd.read_file(tsunami_path)
            if self.tsunami_zones.crs != "EPSG:4326":
                self.tsunami_zones = self.tsunami_zones.to_crs("EPSG:4326")
        else:
            self.tsunami_zones = gpd.GeoDataFrame(geometry=[])

    def check_location(self, lat: float, lon: float):
        """
        Checks location against hazards and finds nearest route.
        """
        user_point = Point(lon, lat)
        
        hazards = []
        nearest_route_info = None

        # Check Tsunami Zones
        if not self.tsunami_zones.empty:
            hits = self.tsunami_zones.contains(user_point)
            if hits.any():
                hazards.append("Tsunami Evacuation Zone")
        
        # Find nearest route regardless of hazard zone (for now, as users might be near one)
        if not self.evac_routes.empty:
            # Calculate distance to all routes (expensive for large datasets, but efficient enough for MVP)
            # Better implementation: use sindex.nearest()
            # unique_index = self.evac_routes.sindex
            
            # Simple distance sorting for now
            distances = self.evac_routes.distance(user_point)
            min_dist_idx = distances.idxmin()
            nearest_route = self.evac_routes.loc[min_dist_idx]
            min_dist_deg = distances.min()
            
            # Approximate conversion deg to meters (at these latitudes ~111km/deg)
            dist_meters = min_dist_deg * 111139 
            
            from shapely.geometry import mapping
            from shapely.ops import nearest_points
            
            # Find the point on the route closest to the user
            # nearest_points returns (pt1, pt2) where pt1 is on geom1 and pt2 is on geom2
            closest_point_on_route = nearest_points(user_point, nearest_route.geometry)[1]
            
            dest_lat = closest_point_on_route.y
            dest_lon = closest_point_on_route.x

            nearest_route_info = {
                "distance_meters": round(dist_meters, 2),
                "name": f"Route in {nearest_route.get('nom_com', 'Unknown')}",
                "description": "Follow marked evacuation signs.",
                "geometry": mapping(nearest_route.geometry),
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
