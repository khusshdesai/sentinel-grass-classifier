# Project Plan and Work Distribution
**Project Title:** Sentinel-2 Satellite Grass & Vegetation Classifier
**Team Size:** 2 Members (Member A & Member B)

## 1. Project Phases (Timeline & Milestones)

**Phase 1: Project Setup & Research (Day 1-2)**
- Finalize tech stack (Python, Streamlit/FastAPI, STAC API).
- Research Earth Search STAC API for Sentinel-2 Level-2A imagery access without auth keys.
- Set up GitHub repository and local development environments.

**Phase 2: Data Acquisition & Backend Core (Day 3-4)**
- Build the connection to the STAC API.
- Implement logic to search for Sentinel-2 images using latitude, longitude, and date range.
- Extract Band 4 (Red) and Band 8 (Near-Infrared).

**Phase 3: Image Processing & Classification (Day 5-7)**
- Implement the NDVI (Normalized Difference Vegetation Index) calculation logic.
- Create masks to threshold NDVI values (e.g., NDVI > 0.3 = Grass/Vegetation).
- Generate visual output images (e.g., color-mapping grass pixels as green).

**Phase 4: API / Application Integration (Day 8-10)**
- Wrap the core processing logic in a web backend (e.g., FastAPI) or an interactive UI (e.g., Streamlit).
- Add error handling for cloudy images or invalid coordinates.

**Phase 5: Testing, Documentation, & Demo Prep (Day 11-12)**
- Test the system with known grassy and non-grassy coordinates (e.g., parks vs. deserts).
- Write the final README documentation (Architecture, API specs, Setup instructions).
- Prepare the presentation and live demo.

---

## 2. Work Distribution

### Member A: Backend, API Integration, & Architecture
*Focuses on fetching the data and serving the application.*
* **Data Fetching:** Implement the `pystac-client` code to query the STAC API and retrieve Sentinel-2 imagery.
* **Backend Development:** Build the REST API (FastAPI) or Streamlit framework to take user inputs (coords/dates).
* **Infrastructure:** Manage the GitHub repo, Python environment, and any Docker configurations.
* **Documentation:** Write the Architecture, Tech Stack, and Setup Instructions in the README.

### Member B: Geospatial Processing & Classification Logic
*Focuses on handling the satellite data and running the classification math.*
* **Data Processing:** Handle loading the STAC assets into `xarray` and `rasterio` format.
* **Algorithm Implementation:** Write the NDVI calculation and the grass thresholding logic.
* **Visualization:** Generate the output imagery (PNG/JPEG) with color-coded grass classifications and percentage statistics using `matplotlib`.
* **Testing:** Find coordinates for edge cases (cloudy days, bodies of water, dense cities) to tune the NDVI thresholds.
