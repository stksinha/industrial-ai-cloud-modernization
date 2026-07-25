# Data Center AI Modernization Gateway

Architecting the Bridge between Legacy & Generative AI for Data Center Infrastructure

## Overview

The **DC AI Modernization Gateway** is an intelligent analysis engine that leverages Google's Generative AI to provide deep insights into data center infrastructure, capacity planning, and power optimization. This application bridges legacy data center monitoring systems with modern AI-driven decision making.

## Features

### 1. **Infrastructure Health Analysis** (`/analyze-dc-metrics`)
Analyzes real-time server and infrastructure metrics to provide:
- Infrastructure health assessment
- Bottleneck identification
- Modernization recommendations
- Risk level classification (Critical/High/Medium/Low)
- Immediate action items (SOP)
- Long-term strategic planning

### 2. **Capacity Planning** (`/capacity-planning`)
Forecasts data center capacity requirements with:
- Current capacity assessment
- 12-month utilization forecasts
- Expansion timeline recommendations
- Hardware/infrastructure upgrade requirements
- Cost-benefit analysis for modernization

### 3. **Power Optimization** (`/power-optimization`)
Optimizes power consumption and cooling efficiency:
- PUE (Power Usage Effectiveness) analysis
- Immediate optimization opportunities
- Long-term efficiency improvements
- Annual energy savings (kWh and cost)
- ROI timeline for recommended upgrades
- Thermal management recommendations

### 4. **Health Check** (`/health`)
Kubernetes-compatible health endpoint

## Deployment

### Local Development
```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="your-google-api-key"
python -m src.app
```

### Docker Deployment
```bash
docker build -t stksinha/industrial-ai-cloud-modernization:latest .
docker run -d -p 5000:5000 \
  -e GOOGLE_API_KEY="your-api-key" \
  stksinha/industrial-ai-cloud-modernization:latest
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s-deployment.yaml
kubectl port-forward -n dc-ai-modernization svc/dc-ai-gateway-svc 5000:80
```

## API Rate Limiting
- **Default limits:** 200 requests/day, 50 requests/hour per IP
- **Analyze DC Metrics:** 10 requests/minute
- **Capacity Planning:** 5 requests/minute
- **Power Optimization:** 8 requests/minute

## Architecture
- 3 replicas by default
- Horizontal Pod Autoscaling (3-10 pods)
- Pod Disruption Budget (minimum 2 available)
- Liveness and readiness probes
- Non-root user execution with read-only filesystem

## Built with
Flask, Marshmallow, Google Generative AI, Kubernetes
