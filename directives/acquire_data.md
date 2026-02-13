# Directive: Acquire Hazard Data

## Goal
Obtain official hazard zone data for Chile to power the safety app.

## Inputs
- **Source**: `https://visorchilepreparado.cl/` (or direct ONEMI/SENAPRED sources).
- **Files Needed**:
    1.  **Tsunami Hazard**:
        - Evacuation Routes (Available locally in `Vías_de_Evacuación_Tsunami/vias_evacuacion.shp`)
        - Evacuation Area (Pending)
        - Meeting Points (Pending)
    2.  **Volcanic Hazard**:
        - Risk Areas (.shp)
        - Meeting Points (.shp)

## Procedure
1.  **Download**: Since direct API access is restricted/complex, download the `.zip` files containing the Shapefiles manually from the viewer if automation fails.
2.  **Storage**: Place the unzipped `.shp` (and related `.dbf`, `.shx`, etc.) files into:
    - `.tmp/data/tsunami/`
    - `.tmp/data/volcano/`
3.  **Verification**: Ensure the Coordinate Reference System (CRS) is standard (e.g., EPSG:4326 or EPSG:32719).

## Outputs
- Valid geospatial files in `.tmp/data/` ready for ingestion by `execution/ingest_data.py`.
