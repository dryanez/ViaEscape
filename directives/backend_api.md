# Directive: Geospatial Backend API

## Goal
Serve an API that accepts a user's geolocation and returns safety instructions.

## Architecture
- **Framework**: FastAPI
- **Port**: 8000

## API Contract
### `POST /api/exclude-hazard`
**Input**:
```json
{
  "lat": -33.4489,
  "lon": -70.6693
}
```

**Logic**:
1.  Create a `Point` geometry from input.
2.  Check if `Point` is inside any **Tsunami Evacuation Zone**.
3.  Check if `Point` is inside any **Volcanic Risk Zone**.
4.  If inside a hazard zone:
    - Find the nearest **Meeting Point**.
    - Return `SAFE: False`, `TYPE: [Hazard Name]`, `DESTINATION: [Lat, Lon]`.
5.  If outside:
    - Return `SAFE: True`.

**Output**:
```json
{
  "safe": false,
  "hazards": ["Tsunami"],
  "nearest_meeting_point": {
    "lat": -33.45,
    "lon": -70.65,
    "name": "Meeting Point #12"
  },
  "message": "You are in a Tsunami Evacuation Zone! Proceed to Meeting Point #12."
}
```

## Tools
- `execution/app.py`: Main application entry point.
- `execution/geospatial_engine.py`: Logic for point-in-polygon and nearest neighbor search.
