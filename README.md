# Sentinel Grass Classifier

A backend service that processes Sentinel-2 satellite imagery via Google Earth Engine to compute Normalized Difference Vegetation Index (NDVI) features for downstream machine learning classification.

## Overview
This project provides an API to fetch and process multi-spectral satellite data based on geographic coordinates and time ranges. It automates the extraction of surface reflectance bands (Red, Near-Infrared) and computes NDVI, returning a visualization thumbnail. The processed data serves as the feature set for a Random Forest classifier (in progress by team members) to distinguish between grass and non-grass surfaces.

### Problem Solved
Manually fetching, filtering, and processing satellite imagery for vegetation mapping is time-consuming and computationally heavy. This API abstracts the Google Earth Engine (GEE) connection, automatically handling temporal and spatial filtering, cloud masking, and feature engineering (NDVI computation), exposing a simple REST endpoint for analysis.

## Architecture & Workflow
1. **Request:** Client submits coordinates and date range via REST API.
2. **Validation:** FastAPI and Pydantic validate inputs (coordinate bounds, strict calendar date formats).
3. **Data Acquisition (GEE):** Connects to the `COPERNICUS/S2_SR_HARMONIZED` dataset.
4. **Preprocessing:** Filters by bounds, dates, and `< 20%` cloud cover. Selects median temporal composite to reduce cloud artifacts.
5. **Feature Engineering:** Computes NDVI using the standard formula `(NIR - Red) / (NIR + Red)`.
6. **Logging:** Reverse geocodes the coordinates (via Nominatim) and logs query metadata to a local CSV asynchronously.
7. **Response:** Returns execution status and an authenticated URL to the generated visualization thumbnail.

*(Note: The Machine Learning inference pipeline using `ee.Classifier.smileRandomForest` is scheduled for the next phase).*

## Tech Stack
- **Framework:** FastAPI
- **Data Source:** Google Earth Engine Python API (`earthengine-api`)
- **Geocoding:** GeoPy (Nominatim)
- **Validation:** Pydantic
- **Environment Management:** Python `venv`, `python-dotenv`

## Project Structure
```text
sentinel-grass-classifier/
├── backend/
│   ├── api.py               # FastAPI entry point, dependency injection, and route handlers
│   ├── core.py              # Earth Engine integration, data fetching, and NDVI math
│   ├── gee_auth.py          # Script to handle local OAuth2 flow for GEE
│   ├── utils.py             # Asynchronous CSV query logging and reverse geocoding
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Template for environment variables
├── work_distribution.md     # Team responsibility breakdown
└── README.md                # Project documentation
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- A Google Cloud Project registered for Earth Engine API access.

### Installation
1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables & Authentication
Instead of hardcoding service accounts, this project relies on local OAuth2 for Earth Engine access to prevent credential leakage.

1. Run the authentication script:
   ```bash
   python gee_auth.py
   ```
2. Follow the browser prompt to authenticate with your Google account. The credentials will be stored locally in `~/.config/earthengine/credentials` (ignored by git).

*(Note: If deploying to a server, you must provide a Service Account JSON key via `.env` instead).*

## Running Locally
Start the FastAPI server with Uvicorn:
```bash
uvicorn api:app --reload
```
The API will be accessible at `http://localhost:8000`. Swagger documentation is available at `http://localhost:8000/docs`.

## API Reference

### `POST /predict`
Analyzes vegetation over a specified geographic point and time range.

**Request Body:**
```json
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "date_start": "2024-01-01",
  "date_end": "2024-05-30"
}
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Data fetched and features computed successfully.",
  "ndvi_thumbnail_url": "https://earthengine.googleapis.com/v1/projects/.../thumbnails/...",
  "coordinates": {
    "lat": 28.6139,
    "lon": 77.2090
  }
}
```

## Engineering Decisions
- **FastAPI BackgroundTasks:** Used for the `log_query_to_csv` function to ensure that network latency from the reverse geocoding API (Nominatim) does not block the main HTTP response to the client.
- **Pydantic `date` Types:** Enforced strict calendar date validation before the request hits the GEE client to prevent opaque remote execution errors.
- **Median Compositing:** Applied `.median()` to the image collection to reduce cloud artifacts and temporal noise across the queried date range.

## Limitations & Future Improvements
- **Rate Limiting:** Geocoding relies on Nominatim's public API, which is strictly rate-limited (1 req/sec). A production environment should swap this for a paid provider or internal lookup table.
- **ML Integration:** The Random Forest classifier training logic is currently handled externally. It needs to be integrated into `core.py` to return predicted class masks rather than raw NDVI gradients.
- **Spatial Expansion:** The API currently expects point coordinates. It should be expanded to accept GeoJSON polygons for bounding-box analysis.