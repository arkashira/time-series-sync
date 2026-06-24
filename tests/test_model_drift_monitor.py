import pytest
import json
from model_drift_monitor import ModelDrift, monitor_model_drift, trigger_alert

def test_model_drift_init():
    model_drift = ModelDrift(threshold=0.5, current_drift=0.2)
    assert model_drift.threshold == 0.5
    assert model_drift.current_drift == 0.2

def test_model_drift_is_drift_exceeded():
    model_drift = ModelDrift(threshold=0.5, current_drift=0.2)
    assert not model_drift.is_drift_exceeded()
    model_drift.update_drift(0.6)
    assert model_drift.is_drift_exceeded()

def test_monitor_model_drift():
    model_drift = ModelDrift(threshold=0.5, current_drift=0.2)
    new_data = [0.3, 0.4, 0.5]
    updated_model_drift = monitor_model_drift(model_drift, new_data)
    assert updated_model_drift.current_drift == sum(new_data) / len(new_data)

def test_trigger_alert():
    model_drift = ModelDrift(threshold=0.5, current_drift=0.2)
    assert trigger_alert(model_drift) == "Model drift within threshold"
    model_drift.update_drift(0.6)
    assert trigger_alert(model_drift) == "Model drift exceeded threshold"

def test_model_drift_to_json():
    model_drift = ModelDrift(threshold=0.5, current_drift=0.2)
    json_str = model_drift.to_json()
    assert json.loads(json_str) == {'threshold': 0.5, 'current_drift': 0.2}
