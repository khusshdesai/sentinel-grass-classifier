import logging
from datetime import date
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from core import process_satellite_data
from utils import log_query_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel-2 Grass Classifier API",
    description="API for fetching satellite imagery and classifying grass vs. non-grass",
    version="1.0.0"
)

# Pydantic models for Input Validation
class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of the location")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of the location")
    date_start: date = Field(..., description="Start date in YYYY-MM-DD format")
    date_end: date = Field(..., description="End date in YYYY-MM-DD format")

class PredictionResponse(BaseModel):
    status: str
    message: str
    ndvi_thumbnail_url: str
    coordinates: dict

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to ensure API is running."""
    return {"status": "healthy", "service": "sentinel-classifier-api"}

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_grass(request: PredictionRequest, background_tasks: BackgroundTasks):
    """
    Accepts coordinates and dates, triggers the core data pipeline, 
    and returns the classification results.
    Logs the query to a CSV file in the background.
    """
    logger.info(f"Received prediction request for coordinates: ({request.latitude}, {request.longitude})")
    
    # Send the logging task to the background so it doesn't block the API response
    background_tasks.add_task(
        log_query_to_csv,
        lat=request.latitude,
        lon=request.longitude,
        date_start=request.date_start.isoformat(),
        date_end=request.date_end.isoformat()
    )
    
    try:
        # Separate Business Logic from the Route Handler
        # We pass validation-checked data to our core processing module
        result = process_satellite_data(
            lat=request.latitude,
            lon=request.longitude,
            date_start=request.date_start.isoformat(),
            date_end=request.date_end.isoformat()
        )
        return result
        
    except ValueError as ve:
        # Handle known business logic errors (e.g., no images found)
        logger.warning(f"Validation/Data error during processing: {ve}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        # Never expose internal errors publicly. Log the real error, return generic 500.
        logger.error(f"Unexpected internal server error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the satellite data."
        )

# Instructions to run:
# uvicorn api:app --reload
