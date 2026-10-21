# ResilAI — Chaos Engineering Framework for AI/ML Systems

Chaos Engineering framework for testing the reliability of AI/ML systems: an
Iris classifier served by a Flask API, containerized with Docker, built and
tested by a Jenkins Freestyle job, verified with Selenium, and subjected to
controlled failure experiments.

## Architecture

```text
Developer / Team
       |
       v
    GitHub
       |
       v
    Jenkins
       |
       +--------------------+
       |                    |
       v                    v
 Automated Tests       Docker Build
       |                    |
       +---------+----------+
                 |
                 v
          Docker Engine
                 |
                 v
        +----------------+
        | AI/ML Container|
        | Flask API      |
        | ML Model       |
        +-------+--------+
                |
                v
       Prediction / Health
                |
                v
       Monitoring & Metrics  <---  Chaos Experiments
                                 (CPU, Memory, Network, Container)
```

See `architecture.md` for full diagrams, `plan.md` for the project plan, and
`implementation.md` for the step-by-step guide.

## Project Structure

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

## Quick Start

### 1. Train the model

```powershell
python app/model.py
```

### 2. Run the API locally

```powershell
python app/app.py
```

Open http://localhost:5000/ and http://localhost:5000/health

### 3. Predict

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/predict `
  -ContentType 'application/json' -Body '{"features":[5.1,3.5,1.4,0.2]}'
```

### 4. Docker

```powershell
docker build -t chaos-ai .
docker run -d -p 5000:5000 --name chaos-ai-container chaos-ai
docker ps
docker logs chaos-ai-container
docker stats
```

Or with Compose:

```powershell
docker compose up -d --build
```

### 5. Tests

```powershell
pytest tests/ -v      # unit + API tests
pytest selenium/ -v   # browser tests (app must be running on :5000)
```

### 6. Jenkins

The active Jenkins job is a Windows Freestyle project. It runs unit tests,
checks the existing Flask service, runs Selenium and all four controlled chaos
experiments, then archives reports. The checked-in
[`jenkins-freestyle-job.xml`](jenkins-freestyle-job.xml) records its build steps.
There is no Groovy Jenkinsfile; configure Jenkins through the Freestyle job.
See [`docs/jenkins-github-setup.md`](docs/jenkins-github-setup.md) for details.

GitHub Actions runs unit tests, Docker build, and browser tests on pushes and
pull requests targeting `main`.

## Chaos Experiments

| # | Experiment | Implementation |
|---|---|---|
| 1 | Container Failure | `chaos/container_failure.md` |
| 2 | CPU Stress | `chaos/cpu_stress.py` |
| 3 | Memory Stress | `chaos/memory_stress.py` |
| 4 | Network Delay | `chaos/network_delay.md` |

Each experiment follows the cycle: establish baseline → form hypothesis →
introduce controlled failure → observe → measure impact → recover → analyze →
improve.

### Run chaos experiments

Interactive menu (user input):

```powershell
python chaos\run_experiments.py
```

```text
========== Chaos Experiments ==========
  1) Container Failure
  2) CPU Stress
  3) Memory Stress
  4) Network Delay
  0) Exit
========================================
Select experiment (0-4):
```

Direct selection (no prompts, used by Jenkins):

```powershell
python chaos\run_experiments.py 1 2 3 4
```

Every experiment saves its measured row to `results/experiment_results.csv`.
Each experiment also runs standalone:

```powershell
python chaos\container_failure.py
python chaos\cpu_stress.py --workers 4 --duration 15 --requests 50
python chaos\memory_stress.py --mb 128 --duration 15 --requests 50
python chaos\network_delay.py --delay 200 --requests 50
```

## Results

Metrics are recorded in `results/experiment_results.csv`:

- Total/successful/failed requests
- Error rate
- Average response time
- CPU / memory usage
- Availability
- Recovery time

## Safety

- Use only an isolated/local test environment.
- Do not target external systems.
- Keep resource experiments controlled; never exhaust host memory.
- Stop experiments if the host becomes unstable.

## Team

| Member | Primary Responsibility |
|---|---|
| Member 1 | AI/ML Model & Flask API |
| Member 2 | Docker & Chaos Engineering |
| Member 3 | Jenkins CI/CD & Selenium |
