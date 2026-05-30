import os
import ee
import logging
from dotenv import load_dotenv

load_dotenv()
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Constants to avoid magic numbers
SENTINEL_2_COLLECTION = 'COPERNICUS/S2_SR_HARMONIZED'
MAX_CLOUD_COVER = 20
BAND_RED = 'B4'
BAND_NIR = 'B8'

def initialize_gee() -> None:
    """Initializes the Google Earth Engine API."""
    project_id = os.getenv("EE_PROJECT_ID")
    if not project_id:
        logger.error("EE_PROJECT_ID environment variable is not set. Please create a .env file and add it.")
        raise ValueError("Missing EE_PROJECT_ID in environment variables.")

    try:
        ee.Initialize(project=project_id)
        logger.info(f"GEE initialized successfully in core with project: {project_id}")
    except Exception as e:
        logger.error(f"Failed to initialize GEE. Please run gee_auth.py first. Error: {e}")
        raise

def get_sentinel2_image(lat: float, lon: float, date_start: str, date_end: str) -> ee.Image:
    """
    Fetches a Sentinel-2 image collection filtered by location, date, and cloud cover,
    and returns the median composite image.
    """
    logger.info(f"Fetching Sentinel-2 image for coords: ({lat}, {lon}) between {date_start} and {date_end}")
    try:
        point = ee.Geometry.Point([lon, lat])
        
        # Filter the image collection
        collection = (ee.ImageCollection(SENTINEL_2_COLLECTION)
                      .filterBounds(point)
                      .filterDate(date_start, date_end)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', MAX_CLOUD_COVER)))
        
        # Check if collection is empty
        count = collection.size().getInfo()
        if count == 0:
            raise ValueError("No images found for the given parameters.")
            
        logger.info(f"Found {count} images. Creating median composite.")
        return collection.median()
        
    except Exception as e:
        logger.error(f"Error fetching Sentinel-2 image: {e}")
        raise

def extract_bands_and_compute_ndvi(image: ee.Image) -> ee.Image:
    """
    Extracts the Red and NIR bands and computes the NDVI feature.
    """
    logger.info("Extracting bands and computing NDVI feature.")
    try:
        # Select the required bands
        bands = image.select([BAND_RED, BAND_NIR])
        
        # Compute NDVI: (NIR - RED) / (NIR + RED)
        ndvi = image.normalizedDifference([BAND_NIR, BAND_RED]).rename('NDVI')
        
        # Add NDVI as a new band to the original image selection
        image_with_features = bands.addBands(ndvi)
        return image_with_features
        
    except Exception as e:
        logger.error(f"Error computing NDVI: {e}")
        raise

def process_satellite_data(lat: float, lon: float, date_start: str, date_end: str) -> Dict[str, Any]:
    """
    Main orchestration function to fetch data and compute features.
    """
    initialize_gee()
    
    # 1. Fetch Image
    image = get_sentinel2_image(lat, lon, date_start, date_end)
    
    # 2. Extract bands and compute NDVI feature
    feature_image = extract_bands_and_compute_ndvi(image)
    
    # For now, we will return a thumbnail URL as proof of successful processing
    # In Phase 3, this is where we would pass the data to the Random Forest model
    try:
        point = ee.Geometry.Point([lon, lat])
        buffer_region = point.buffer(1000) # 1km buffer around the point
        
        url = feature_image.select('NDVI').getThumbURL({
            'min': -1,
            'max': 1,
            'dimensions': 512,
            'region': buffer_region,
            'palette': ['blue', 'white', 'green']
        })
        
        logger.info("Successfully generated NDVI thumbnail URL.")
        return {
            "status": "success",
            "message": "Data fetched and features computed successfully.",
            "ndvi_thumbnail_url": url,
            "coordinates": {"lat": lat, "lon": lon}
        }
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        raise
