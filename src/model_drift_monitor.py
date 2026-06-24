import json
from dataclasses import dataclass
from typing import List

@dataclass
class ModelDrift:
    threshold: float
    current_drift: float

    def is_drift_exceeded(self) -> bool:
        return self.current_drift > self.threshold

    def update_drift(self, new_drift: float) -> None:
        self.current_drift = new_drift

    def to_json(self) -> str:
        return json.dumps({
            'threshold': self.threshold,
            'current_drift': self.current_drift
        })

def monitor_model_drift(model_drift: ModelDrift, new_data: List[float]) -> ModelDrift:
    # Simple example of calculating drift, replace with actual implementation
    new_drift = sum(new_data) / len(new_data)
    model_drift.update_drift(new_drift)
    return model_drift

def trigger_alert(model_drift: ModelDrift) -> str:
    if model_drift.is_drift_exceeded():
        return "Model drift exceeded threshold"
    else:
        return "Model drift within threshold"
