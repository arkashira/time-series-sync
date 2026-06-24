# Model Drift Monitor
A simple Python project for monitoring model drift.

## Usage
1. Create a `ModelDrift` object with a threshold and initial drift value.
2. Use the `monitor_model_drift` function to update the drift value with new data.
3. Use the `trigger_alert` function to check if the drift has exceeded the threshold.

## Testing
Run the tests using `pytest`:
