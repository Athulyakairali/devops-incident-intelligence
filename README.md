# 🚨 DevOps Incident Intelligence Platform

An automated DevOps incident detection and root-cause analysis platform that monitors Kubernetes workloads, detects container incidents, collects logs and Kubernetes events, and uses a local LLM to generate evidence-based Root Cause Analysis (RCA).

## 🏗️ Architecture

```text
GitHub
   │
   ▼
Jenkins CI/CD
   │
   ├── Unit Tests
   ├── Docker Build
   ├── Trivy Security Scan
   │
   ▼
Docker Image
   │
   ▼
Minikube / Kubernetes
   │
   ▼
Incident Intelligence Platform
   │
   ├── Incident Detection
   ├── Pod Logs
   ├── Kubernetes Events
   │
   ▼
Incident Analyzer
   │
   ▼
Ollama + Qwen 2.5 7B
   │
   ▼
Root Cause Analysis
   ├── Root Cause
   ├── Confirmed Evidence
   ├── Contributing Factors
   ├── Unknowns
   └── Recommendations
```

## ✨ Features

- Automated Kubernetes incident detection
- OOMKilled detection
- CrashLoopBackOff detection
- ImagePullBackOff detection
- ErrImagePull detection
- Container error detection
- Kubernetes pod log collection
- Kubernetes event collection
- AI-powered Root Cause Analysis
- Evidence-based incident analysis
- Flask REST API
- Docker containerization
- Minikube Kubernetes deployment
- Jenkins CI/CD pipeline
- Trivy container security scanning
- Automated unit tests

## 🔍 Supported Incidents

| Kubernetes Condition | Incident Type |
|---|---|
| `OOMKilled` | `MEMORY_EXHAUSTION` |
| `CrashLoopBackOff` | `CONTAINER_CRASH_LOOP` |
| `ImagePullBackOff` | `IMAGE_PULL_FAILURE` |
| `ErrImagePull` | `IMAGE_PULL_FAILURE` |
| `Error` | `CONTAINER_ERROR` |

## 🤖 AI-Powered Root Cause Analysis

The platform uses **Ollama** with **Qwen 2.5 7B** to analyze detected incidents.

The RCA engine considers:

- Kubernetes incident reason
- Container exit code
- Pod status
- Memory limits
- Application logs
- Kubernetes events

The generated report contains:

- Root cause
- Confirmed evidence
- Likely contributing factors
- Unknown / unconfirmed information
- Recommended actions
- Confidence

The RCA process is designed to distinguish confirmed evidence from assumptions.

## 💥 Incident Simulation

The project includes an intentional Kubernetes memory-stress pod.

The pod has a memory limit of:

```text
50Mi
```

The container continuously allocates memory until Kubernetes terminates it.

Expected result:

```text
OOMKilled
Exit Code: 137
```

Example detected incident:

```json
{
  "type": "MEMORY_EXHAUSTION",
  "reason": "OOMKilled",
  "exit_code": 137,
  "pod": "memory-stress",
  "container": "memory-stress"
}
```

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Flask | REST API |
| Kubernetes Python Client | Kubernetes integration |
| Kubernetes | Container orchestration |
| Minikube | Local Kubernetes cluster |
| Docker | Containerization |
| Ollama | Local LLM runtime |
| Qwen 2.5 7B | Root Cause Analysis |
| Jenkins | CI/CD automation |
| Trivy | Container security scanning |
| GitHub | Version control |
| unittest | Automated testing |

## 📁 Project Structure

```text
devops-incident-intelligence/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
├── .gitignore
│
├── engine/
│   ├── __init__.py
│   ├── detector.py
│   ├── events.py
│   ├── logs.py
│   ├── analyzer.py
│   └── rca.py
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── memory-stress.yaml
│
└── tests/
    └── test_detector.py
```

## 🚀 Getting Started

### Prerequisites

Install:

- Python 3.12+
- Docker
- kubectl
- Minikube
- Ollama
- Git

For CI/CD:

- Jenkins
- Trivy

### 1. Clone the Repository

```bash
git clone https://github.com/Athulyakairali/devops-incident-intelligence.git
cd devops-incident-intelligence
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Minikube

```bash
minikube start --driver=docker
```

Verify:

```bash
kubectl get nodes
```

### 5. Start Ollama

Make sure Ollama is running:

```bash
ollama serve
```

Pull the model if required:

```bash
ollama pull qwen2.5:7b
```

Verify:

```bash
ollama list
```

### 6. Deploy the Kubernetes Application

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Verify:

```bash
kubectl get pods
kubectl get services
```

## 💣 Reproduce an Incident

Deploy the intentional memory stress pod:

```bash
kubectl apply -f k8s/memory-stress.yaml
```

Check its status:

```bash
kubectl get pods
```

Expected:

```text
memory-stress    0/1    OOMKilled
```

## 🔎 Run the Incident Detector

```bash
python -m engine.detector
```

Example:

```text
INCIDENTS DETECTED

{
  "type": "MEMORY_EXHAUSTION",
  "reason": "OOMKilled",
  "exit_code": 137,
  "pod": "memory-stress",
  "container": "memory-stress"
}
```

## 📊 Run the Incident Analyzer

```bash
python -m engine.analyzer
```

The analyzer combines:

```text
Incident
   +
Pod Details
   +
Kubernetes Events
   +
Application Logs
   ↓
Root Cause Analysis
```

## 🌐 Flask API

Start the application:

```bash
python app.py
```

The API runs on:

```text
http://127.0.0.1:5000
```

### Health Check

```bash
curl http://127.0.0.1:5000/health
```

Response:

```json
{
  "status": "healthy"
}
```

### Get Incidents

```bash
curl http://127.0.0.1:5000/incidents
```

Example response:

```json
{
  "count": 1,
  "incidents": [
    {
      "incident_id": "INC-001",
      "pod": "memory-stress",
      "container": "memory-stress",
      "incident_type": "MEMORY_EXHAUSTION",
      "reason": "OOMKilled",
      "exit_code": 137,
      "memory_limit": "50Mi",
      "pod_status": "Failed",
      "severity": "HIGH"
    }
  ]
}
```

### Get a Specific Incident

```bash
curl http://127.0.0.1:5000/incidents/INC-001
```

## 🐳 Docker

Build the image:

```bash
docker build -t incident-intelligence:test .
```

Run the container:

```bash
docker run --rm -d \
  --name incident-intelligence-test \
  -p 5001:5000 \
  -e KUBERNETES_IN_CLUSTER=true \
  -e KUBERNETES_API_SERVER=https://host.docker.internal:63935 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -v ~/.minikube/ca.crt:/certs/ca.crt:ro \
  -v ~/.minikube/profiles/minikube/client.crt:/certs/client.crt:ro \
  -v ~/.minikube/profiles/minikube/client.key:/certs/client.key:ro \
  --add-host=host.docker.internal:host-gateway \
  incident-intelligence:test
```

Test:

```bash
curl http://127.0.0.1:5001/health
```

```bash
curl http://127.0.0.1:5001/incidents
```

## 🔄 CI/CD Pipeline

Jenkins automates the following workflow:

```text
Checkout
   ↓
Create Python Virtual Environment
   ↓
Install Dependencies
   ↓
Compile Python Files
   ↓
Run Unit Tests
   ↓
Build Docker Image
   ↓
Trivy Security Scan
   ↓
Load Image into Minikube
   ↓
Deploy to Kubernetes
   ↓
Restart Deployment
   ↓
Verify Rollout
```

## 🧪 Automated Testing

Run the test suite locally:

```bash
python -m unittest discover -s tests -v
```

The current test suite covers:

- OOMKilled
- Container Error
- CrashLoopBackOff
- ImagePullBackOff
- ErrImagePull
- Unknown container states

Expected result:

```text
Ran 6 tests

OK
```

## 🔐 Security Scanning

The Jenkins pipeline uses Trivy to scan the Docker image for high and critical vulnerabilities.

```bash
trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  incident-intelligence:ci
```

The pipeline fails if vulnerabilities meeting the configured severity threshold are detected.

## 🔁 Incident Intelligence Workflow

```text
Kubernetes Incident
        ↓
Incident Detection
        ↓
Pod State Analysis
        ↓
Log Collection
        ↓
Kubernetes Event Collection
        ↓
Incident Analyzer
        ↓
Ollama + Qwen 2.5
        ↓
Root Cause Analysis
        ↓
Evidence + Recommendations
```

## 🎯 Project Goals

This project demonstrates practical implementation of:

- Kubernetes monitoring
- Automated incident detection
- Container failure analysis
- Log and event collection
- AI-assisted root-cause analysis
- Docker containerization
- CI/CD automation
- Container security scanning
- Local Kubernetes development
- Automated testing

## 👩‍💻 Author

**Athulya Kairali**

GitHub: [Athulyakairali](https://github.com/Athulyakairali)

---

⭐ If you found this project interesting, consider giving the repository a star!
