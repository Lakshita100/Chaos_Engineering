# Chaos Engineering for AI Systems — Implementation Guide

## 1. Environment
Use:
- Windows
- VS Code
- Python
- Git/GitHub
- Docker Desktop
- Jenkins
- Chrome
- Selenium

## 2. Project Structure

```text
chaos-engineering-ai/
├── app/
│   ├── app.py
│   ├── model.py
│   └── requirements.txt
├── model/
│   └── model.pkl
├── tests/
│   ├── test_api.py
│   └── test_model.py
├── selenium/
│   └── test_prediction.py
├── chaos/
│   ├── cpu_stress.py
│   ├── memory_stress.py
│   ├── network_delay.md
│   └── container_failure.md
├── results/
│   └── experiment_results.csv
├── Dockerfile
├── docker-compose.yml
├── jenkins-freestyle-job.xml
├── .gitignore
└── README.md
```

## 3. Team Responsibilities

### Member 1 — AI/ML + API
- Iris dataset
- Model training
- Model serialization
- Flask API
- Validation
- API tests

### Member 2 — Docker + Chaos
- Dockerfile
- Docker image/container
- Docker Compose if required
- Container failure
- CPU stress
- Memory stress
- Network delay
- Metrics

### Member 3 — Jenkins Freestyle + Selenium
- Maintain the local GitHub checkout used by the job
- Freestyle build steps
- Windows batch commands
- Selenium tests
- Build results

### Shared
- Git commits
- Documentation
- Results
- Report
- PPT
- Viva

## 4. Create Repository

```powershell
mkdir chaos-engineering-ai
cd chaos-engineering-ai
git init
git branch -M main
```

Create the project structure, then:

```powershell
git add .
git commit -m "Initial project structure"
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## 5. Python Environment

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

Install:

```powershell
pip install flask scikit-learn pandas numpy pytest selenium joblib
pip freeze > requirements.txt
```

## 6. ML Model

Use the Iris dataset and Random Forest.

Workflow:

```text
Load Dataset
    ↓
Split Data
    ↓
Train Random Forest
    ↓
Evaluate
    ↓
Save model.pkl
```

Store the model in:

```text
model/model.pkl
```

## 7. Flask API

Required endpoints:

### GET `/`
Service running message.

### GET `/health`
Example:

```json
{"status": "healthy"}
```

### POST `/predict`
Example input:

```json
{"features": [5.1, 3.5, 1.4, 0.2]}
```

Validate:
- JSON exists
- `features` exists
- Exactly four numeric values

Invalid input should return a useful error instead of crashing.

## 8. Local Testing

Run:

```powershell
python app/app.py
```

Open:

```text
http://localhost:5000/
http://localhost:5000/health
```

Test `/predict` using Postman, curl, or another API client.

## 9. Docker

Build:

```powershell
docker build -t chaos-ai .
```

Run:

```powershell
docker run -d -p 5000:5000 --name chaos-ai-container chaos-ai
```

Check:

```powershell
docker ps
docker logs chaos-ai-container
docker stats
```

## 10. Automated Tests

Minimum tests:
1. Root endpoint
2. Health endpoint
3. Valid prediction
4. Invalid input
5. Prediction response

Run:

```powershell
pytest
```

## 11. Selenium

Test:
1. Open application
2. Verify page
3. Enter valid values
4. Trigger prediction
5. Verify result
6. Test invalid input

Run Selenium automatically through Jenkins after starting the application.

## 12. Jenkins Freestyle Job

The Windows Freestyle job uses the local repository checkout and the existing
Docker service on port 5000. Its build steps are:

```text
Install Dependencies
  ↓
Unit Tests
  ↓
Health Check
  ↓
Selenium Tests
  ↓
Chaos Experiments 1–4
  ↓
Copy and Archive Results
```

Use `jenkins-freestyle-job.xml` as the Freestyle build-step reference. The job
does not use a Groovy Jenkinsfile or rebuild the running Docker container.

## 13. Baseline

Before chaos, use a fixed workload such as 100 requests.

Record:
- Total requests
- Successful requests
- Failed requests
- Average response time
- CPU usage
- Memory usage
- Availability

Use actual measurements in the final report.

## 14. Chaos Experiment 1 — Container Failure

Hypothesis:

> If the AI container stops unexpectedly, the prediction service becomes unavailable until the service is restored.

Procedure:
1. Start container.
2. Verify `/health`.
3. Send requests.
4. Stop container.
5. Send requests again.
6. Record failures.
7. Restart container.
8. Verify health.
9. Record recovery time.

Commands:

```powershell
docker stop chaos-ai-container
docker start chaos-ai-container
```

## 15. Chaos Experiment 2 — CPU Stress

Hypothesis:

> Increased CPU utilization increases response time and may reduce throughput.

Procedure:
1. Establish baseline.
2. Introduce controlled CPU stress.
3. Monitor `docker stats`.
4. Run the same workload.
5. Record response time/errors.
6. Stop stress.
7. Verify recovery.

Keep resource limits controlled.

## 16. Chaos Experiment 3 — Memory Stress

Hypothesis:

> Increased memory pressure may cause performance degradation or service failure.

Procedure:
1. Establish baseline.
2. Introduce controlled memory stress.
3. Monitor memory.
4. Run workload.
5. Record metrics.
6. Remove stress.
7. Verify recovery.

Never intentionally exhaust the host system's memory.

## 17. Chaos Experiment 4 — Network Delay

Hypothesis:

> Increased network latency increases end-to-end prediction response time.

Procedure:
1. Measure normal response time.
2. Introduce controlled delay.
3. Send the same workload.
4. Record latency/errors.
5. Remove delay.
6. Verify normal behavior.

## 18. Optional AI-Specific Experiment

Compare a valid input with a slightly perturbed input:

```text
Original:  [5.1, 3.5, 1.4, 0.2]
Perturbed: [5.2, 3.4, 1.5, 0.2]
```

Compare predictions. Treat this as an exploratory robustness test.

## 19. Results CSV

Suggested columns:

```text
Experiment
TotalRequests
SuccessfulRequests
FailedRequests
ErrorRate
AverageResponseTime
CPUUsage
MemoryUsage
RecoveryTime
Availability
Remarks
```

## 20. Git Workflow

Each member can use a branch:

```text
main
├── member1-ml-api
├── member2-docker-chaos
└── member3-jenkins-selenium
```

Example:

```powershell
git checkout -b feature-name
git add .
git commit -m "Meaningful change"
git push -u origin feature-name
```

Merge tested changes into `main`.

## 21. Final Demo

1. GitHub
2. ML model
3. Docker container
4. Prediction
5. Jenkins Freestyle build
6. Selenium test
7. Baseline metrics
8. Chaos experiment
9. Failure/degradation
10. Recovery
11. Results
12. Conclusion

## 22. Safety

- Use only an isolated/local test environment.
- Do not target external systems.
- Keep resource experiments controlled.
- Stop experiments if the host becomes unstable.
