document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('loadingSpinner');
    const resultsPanel = document.getElementById('resultsPanel');

    // UI Loading State
    btnText.textContent = 'Processing...';
    spinner.classList.remove('hidden');
    submitBtn.disabled = true;
    resultsPanel.classList.add('hidden');

    const payload = {
        latitude: document.getElementById('latitude').value,
        longitude: document.getElementById('longitude').value,
        date_start: document.getElementById('date_start').value,
        date_end: document.getElementById('date_end').value
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred during prediction.');
        }

        // Populate Results
        document.getElementById('resPrediction').textContent = data.prediction;
        
        // Change color based on grass
        if (data.is_grass) {
            document.getElementById('resPrediction').style.color = '#00f2fe';
        } else {
            document.getElementById('resPrediction').style.color = '#ff6b6b';
        }

        document.getElementById('resConfidence').textContent = `${data.confidence.toFixed(1)}%`;
        document.getElementById('resPercentage').textContent = `${data.grass_percentage.toFixed(1)}%`;
        document.getElementById('resNdvi').textContent = data.ndvi_mean.toFixed(3);
        
        // Append a timestamp query parameter to bypass browser image caching for new predictions
        const timestamp = new Date().getTime();
        document.getElementById('resMap').src = `${data.visualization_path}?t=${timestamp}`;
        document.getElementById('resNdviMap').src = data.ndvi_thumbnail_url;

        // Show Results
        resultsPanel.classList.remove('hidden');

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        // Reset UI
        btnText.textContent = 'Analyze Terrain';
        spinner.classList.add('hidden');
        submitBtn.disabled = false;
    }
});
