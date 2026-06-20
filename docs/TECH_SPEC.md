# TECH_SPEC.md – time‑series‑sync

**Document version**: 1.0  
**Last updated**: 2026‑06‑20  
**Owner**: Senior Product/Engineering Lead – Axentx  

---  

## 1. Overview  

`time-series-sync` is a **scalable, production‑grade time‑series forecasting service** that can be embedded in any data‑science workflow. It provides:

* **High‑throughput inference** via the **vLLM** inference engine (GPU‑accelerated transformer serving).  
* **Structured forecast generation** (point forecasts, confidence intervals, quantile forecasts) powered by **SGLang** for deterministic, token‑level control.  
* **Zero‑copy data exchange** with popular Python data‑science stacks (pandas, Dask, PySpark, Polars).  
* **Multi‑tenant SaaS‑style deployment** (per‑customer model isolation, quota enforcement, audit logging).  

The service is delivered as a **Docker‑based microservice** exposing both a **RESTful HTTP API** and a **Python SDK**. All components are orchestrated on Kubernetes (GKE/EKS/AKS) with autoscaling based on request volume and GPU utilization.

---  

## 2. Architecture  

```
+-------------------+      +-------------------+      +-------------------+
|   Client Apps     | ---> |   API Gateway     | ---> |   AuthZ Service   |
+-------------------+      +-------------------+      +-------------------+
                                 |
                                 v
+-------------------+   +-------------------+   +-------------------+
|   Python SDK     |   |   REST / gRPC     |   |   Metrics / Logs  |
+-------------------+   +-------------------+   +-------------------+
                                 |
                                 v
+-----------------------------------------------------------+
|                     Inference Service                     |
|  +-------------------+   +-------------------+            |
|  |  vLLM Engine      |   |  SGLang Generator |            |
|  +-------------------+   +-------------------+            |
|            |                     |                      |
|            v                     v                      |
|  +-------------------+   +-------------------+            |
|  |  Model Store (S3) |   |  Config Store (Etc) |          |
|  +-------------------+   +-------------------+            |
+-----------------------------------------------------------+
                                 |
                                 v
+-------------------+   +-------------------+   +-------------------+
|   Model Trainer   |   |   Data Ingestor   |   |   Monitoring      |
| (offline, Spark) |   | (Kafka / Kinesis)|   | (Prometheus)      |
+-------------------+   +-------------------+   +-------------------+
```

### 2.1 Core Components  

| Component | Responsibility | Tech |
|-----------|----------------|------|
| **API Gateway** | TLS termination, request routing, rate‑limiting, request/response transformation | **Envoy** (sidecar) |
| **AuthZ Service** | JWT validation, per‑tenant quota enforcement, RBAC | **Keycloak** |
| **Inference Service** | Serves forecasts; orchestrates vLLM and SGLang | **FastAPI** (Python 3.11) |
| **vLLM Engine** | High‑throughput transformer inference (e.g., `TimeGPT`, `Chronos`) | **vLLM** (v0.4+) |
| **SGLang Generator** | Structured output (JSON, CSV) with token‑level constraints | **SGLang** (v0.2+) |
| **Model Store** | Versioned model artifacts (weights, config) | **Amazon S3** (or GCS) + **mlflow** tracking |
| **Config Store** | JSON/YAML model‑specific hyper‑parameters, feature schema | **etcd** |
| **Model Trainer** | Offline batch training, hyper‑parameter search | **Spark‑ML**, **PyTorch Lightning**, **Ray Tune** |
| **Data Ingestor** | Real‑time time‑series ingestion, schema validation | **Kafka** (or **Kinesis**) + **Schema Registry** |
| **Monitoring** | Metrics, traces, logs, alerting | **Prometheus**, **Grafana**, **OpenTelemetry** |
| **Python SDK** | Convenience wrapper for REST/gRPC, pandas‑compatible `predict` | **requests**, **pydantic**, **pandas** |

---  

## 3. Data Model  

### 3.1 Input Payload  

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `tenant_id` | `string` | Unique identifier for the customer (must match JWT `sub`) | Required |
| `series_id` | `string` | Logical identifier of the time‑series (e.g., sensor ID) | Required |
| `timestamp` | `int64` (epoch ms) | End of the observed window | Required |
| `features` | `object` | Mapping of feature name → numeric value (including target) | At least one feature required |
| `metadata` *(optional)* | `object` | Arbitrary key/value pairs (e.g., location, tags) | – |

**Example (JSON)**  

```json
{
  "tenant_id": "acme-corp",
  "series_id": "sensor-42",
  "timestamp": 1729507200000,
  "features": {
    "value": 12.7,
    "temp": 23.1,
    "humidity": 48.2
  },
  "metadata": {
    "region": "us-east-1"
  }
}
```

### 3.2 Output Payload
