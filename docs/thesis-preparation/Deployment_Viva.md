# MindShield — Deployment & Cloud Infrastructure Viva Guide

> **Module**: Production Deployment, Containerisation & CI/CD Strategy  
> **Focus**: Uvicorn/Gunicorn, Nginx, Docker, Kubernetes, CI/CD Pipelines, Multi-Phase Roadmap  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding

### Q1: What is the recommended production deployment stack for the MindShield FastAPI backend?
**Model Answer:**  
The production stack uses a layered reverse-proxy and process-manager architecture:
1. **Nginx**: Acts as the SSL/TLS termination proxy, static file server, and DDoS protection layer.
2. **Gunicorn**: Functions as the process manager (`gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`), managing worker lifecycle and auto-restarting crashed processes.
3. **Uvicorn Workers**: Execute the async FastAPI application on ASGI event loops.
4. **Redis**: Handles rate limiting and distributed caching.

---

### Q2: What is the multi-phase backend development roadmap for MindShield?
**Model Answer:**  

| Phase | Target Deliverable | Status |
|---|---|:---:|
| **Phase 2.1** | FastAPI foundation, Pydantic v2 schemas, `BaseModelLoader`, 71 tests | ✅ Complete |
| **Phase 2.2** | Real ML model integration (`BertModelLoader` / `TfIdfSvmModelLoader`) | Planned |
| **Phase 2.3** | Async worker offloading via Celery / Redis | Planned |
| **Phase 2.4** | Server-side PostgreSQL database persistence | Planned |
| **Phase 2.5** | OAuth2 / JWT authentication & API Key management | Planned |
| **Phase 2.6** | Per-IP sliding-window rate limiting | Planned |
| **Phase 2.7** | Batch analysis endpoint (`POST /api/v1/analyze/batch`) | Planned |
| **Phase 2.8** | Docker & Docker Compose containerisation | Planned |
| **Phase 2.9** | Prometheus metrics & Grafana monitoring dashboards | Planned |

---

## Section B — Design Decision Justification

### Q3: Why containerise the backend using Docker?
**Model Answer:**  
Containerisation encapsulates Python 3.13 binaries, PyTorch/Transformers dependencies, C-extensions, and configuration files into an immutable container image. This eliminates "works on my machine" issues across developer OS environments (Windows/Linux/macOS) and production cloud nodes, while enabling seamless horizontal scaling in cloud environments (AWS ECS / Kubernetes).

---

## Section C — Implementation & Technical Depth

### Q4: Outline the target multi-stage Dockerfile structure.
**Model Answer:**  
```dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ app/
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Section D — Limitations, Risks & Future Work

### Q5: How will cloud hosting costs and latency be managed for mobile users?
**Model Answer:**  
Deploying deep learning models on cloud GPUs (e.g. AWS g4dn instances) incurs high operational costs. To mitigate this:
1. **Edge Inference**: Quantized ONNX/TFLite models will run locally on Android devices for immediate classification.
2. **Cloud Fallback**: Cloud APIs will be invoked only for high-uncertainty samples or when detailed LIME explainability breakdowns are requested.
3. **CDNs / Regional Edge**: Cloud endpoints will be deployed in regional data centers close to user populations to minimize round-trip network latency.

---
*MindShield Deployment Viva Guide · Final Year Project 2026*
