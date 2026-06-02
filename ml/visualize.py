import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

def generate_prediction_visual(
    ndvi_array: np.ndarray,
    grass_mask_2d: np.ndarray,
    grass_percentage: float,
    confidence: float,
    lat: float,
    lon: float,
) -> str:
    """
    Generates a color-coded PNG using the true Machine Learning 2D prediction mask.
    Returns: Path to the saved image.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#1a1a2e')

    # --- Left: NDVI heatmap ---
    ax1 = axes[0]
    ndvi_plot = ax1.imshow(ndvi_array, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(ndvi_plot, ax=ax1, label='NDVI Value')
    ax1.set_title('NDVI Map', color='white', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Pixel (X)', color='white')
    ax1.set_ylabel('Pixel (Y)', color='white')
    ax1.tick_params(colors='white')

    # --- Right: True ML Prediction map ---
    ax2 = axes[1]

    # Use the actual ML model's prediction mask!
    color_map = np.zeros((*ndvi_array.shape, 3))
    color_map[grass_mask_2d] = [0.2, 0.8, 0.2]       # green = grass
    color_map[~grass_mask_2d] = [0.6, 0.4, 0.2]      # brown = non-grass

    ax2.imshow(color_map)
    ax2.set_title('Grass Detection Map (ML Predicted)', color='white', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Pixel (X)', color='white')
    ax2.set_ylabel('Pixel (Y)', color='white')
    ax2.tick_params(colors='white')

    # Legend
    grass_patch = mpatches.Patch(color='#33cc33', label='Grass')
    non_grass_patch = mpatches.Patch(color='#996633', label='Non-Grass')
    ax2.legend(handles=[grass_patch, non_grass_patch],
               loc='lower right', facecolor='#1a1a2e', labelcolor='white')

    # Overall prediction text
    prediction_text = "GRASS DOMINANT" if grass_percentage > 20 else "NON-GRASS"
    color = '#33cc33' if grass_percentage > 20 else '#ff4444'
    fig.suptitle(
        f'Prediction: {prediction_text} ({grass_percentage:.1f}% Area) | Confidence: {confidence}%\n'
        f'Coordinates: ({lat}, {lon})',
        color=color, fontsize=14, fontweight='bold', y=1.02
    )

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prediction_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()

    logger.info(f"Visualization saved: {output_path}")
    return output_path