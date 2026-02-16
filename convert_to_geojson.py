import geopandas as gpd
import os

import geopandas as gpd
import os

files_to_convert = [
    {
        "shp": "Vías_de_Evacuación_Tsunami/vias_evacuacion.shp",
        "out": "api/vias_evacuacion.geojson"
    },
    {
        "shp": "Áreas_de_Evacuación_Tsunami/Áreas_de_Evacuación_Tsunami.shp",
        "out": "api/areas_evacuacion.geojson"
    },
    {
        "shp": "Puntos_de_Encuentro_Tsunami/puntos_encuentro.shp",
        "out": "api/puntos_encuentro.geojson"
    }
]

for item in files_to_convert:
    shp_path = item["shp"]
    geojson_path = item["out"]

    if os.path.exists(shp_path):
        try:
            print(f"Reading {shp_path}...")
            gdf = gpd.read_file(shp_path)
            
            # Ensure EPSG:4326
            if gdf.crs != "EPSG:4326":
                print("Converting to EPSG:4326...")
                gdf = gdf.to_crs("EPSG:4326")
            
            # Simplify geometry to reduce file size for Vercel (optional but recommended)
            # gdf['geometry'] = gdf.simplify(0.0001) 

            print(f"Writing to {geojson_path}...")
            gdf.to_file(geojson_path, driver="GeoJSON")
            print("Done!")
        except Exception as e:
            print(f"Error processing {shp_path}: {e}")
    else:
        print(f"Shapefile not found: {shp_path}")
