from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .geospatial_engine import engine
import uvicorn

app = FastAPI()

class Location(BaseModel):
    lat: float
    lon: float

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.post("/api/check-hazard")
def check_hazard(location: Location):
    try:
        result = engine.check_location(location.lat, location.lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
