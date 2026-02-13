import geopandas as gpd
import os

shp_path = "Vías_de_Evacuación_Tsunami/vias_evacuacion.shp"
geojson_path = "execution/vias_evacuacion.geojson"

if os.path.exists(shp_path):
    try:
        print(f"Reading {shp_path}...")
        gdf = gpd.read_file(shp_path)
        
        # Ensure EPSG:4326
        if gdf.crs != "EPSG:4326":
            print("Converting to EPSG:4326...")
            gdf = gdf.to_crs("EPSG:4326")
            
        print(f"Writing to {geojson_path}...")
        gdf.to_file(geojson_path, driver="GeoJSON")
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Shapefile not found.")
