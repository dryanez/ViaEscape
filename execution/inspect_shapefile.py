import geopandas as gpd
import os

path = "Vías_de_Evacuación_Tsunami/vias_evacuacion.shp"

if not os.path.exists(path):
    print(f"File not found: {path}")
else:
    try:
        df = gpd.read_file(path)
        print(f"CRS: {df.crs}")
        print(f"Geometry Type: {df.geom_type.unique()}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"First 5 rows:\n{df.head()}")
    except Exception as e:
        print(f"Error reading file: {e}")
