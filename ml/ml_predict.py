import os
import pickle
import numpy as np
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')

def load_model():
    """Load the pixel-level saved model."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run train.py first.")
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    return model

def compute_ndvi(red, nir):
    """NDVI = (NIR - Red) / (NIR + Red)"""
    denominator = nir + red
    ndvi = np.where(denominator == 0, 0, (nir - red) / denominator)
    return ndvi

def predict_grass(red_band: np.ndarray, nir_band: np.ndarray) -> dict:
    """
    Accepts 2D Red and NIR band arrays and predicts grass pixel-by-pixel.
    Returns the 2D boolean grass mask, along with overall statistics.
    """
    model = load_model()

    red = red_band.astype(np.float32)
    nir = nir_band.astype(np.float32)
    ndvi = compute_ndvi(red, nir)
    
    # Flatten the 2D arrays into 1D for batch prediction
    flat_red = red.flatten()
    flat_nir = nir.flatten()
    flat_ndvi = ndvi.flatten()
    
    # Create (N, 3) feature matrix for the whole image
    features = np.column_stack((flat_red, flat_nir, flat_ndvi))
    
    # Predict all pixels at once (1 = Grass, 0 = Non-Grass)
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1] # Probability of Grass (Class 1)
    
    # Reshape back to original 2D image dimensions
    grass_mask_2d = predictions.reshape(red.shape).astype(bool)
    
    # Calculate overall stats for the region
    total_pixels = len(predictions)
    grass_pixels = np.sum(predictions == 1)
    grass_percentage = (grass_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    avg_confidence = float(np.mean(probabilities)) * 100
    
    result = {
        "prediction": "Grass" if grass_percentage > 20 else "Non-Grass", # Arbitrary overall label
        "is_grass": bool(grass_percentage > 20),
        "confidence": round(avg_confidence, 2),
        "grass_percentage": round(grass_percentage, 2),
        "ndvi_mean": round(float(np.mean(ndvi)), 4),
        "grass_mask_2d": grass_mask_2d,
        "ndvi_array": ndvi
    }

    logger.info(f"Pixel-level Prediction Complete: {grass_percentage:.2f}% of the area is grass.")
    return result

if __name__ == "__main__":
    # Simple test with dummy data
    dummy_red = np.random.rand(100, 100) * 1000
    dummy_nir = np.random.rand(100, 100) * 1500
    try:
        res = predict_grass(dummy_red, dummy_nir)
        print("Success! Grass percentage:", res['grass_percentage'])
    except Exception as e:
        print("Error:", e)