# Chaos Engineering for AI Systems — Project Plan

## 1. Project Title
**Chaos Engineering Framework for Testing the Reliability of AI/ML Systems**

## 2. Team
3-member team.

| Member | Primary Responsibility | Supporting Responsibilities |
|---|---|---|
| Member 1 | AI/ML Model & Flask API | Testing, documentation |
| Member 2 | Docker & Chaos Engineering | Monitoring, experiments |
| Member 3 | Jenkins CI/CD & Selenium | GitHub integration, testing |

All members should understand the complete architecture for the viva.

## 3. Goal
Develop a simple AI/ML prediction service, containerize it using Docker, integrate GitHub and Jenkins CI/CD, test it using Selenium, and intentionally introduce controlled failures to study reliability and resilience.

## 4. Technologies
- Python
- Scikit-learn
- Flask
- Git/GitHub
- Docker
- Jenkins
- Selenium
- Pytest
- CSV/JSON for results

## 5. Project Phases
### Phase 1 — Setup
- GitHub repository
- Project structure
- Python environment
- Git workflow

### Phase 2 — ML Model
- Iris dataset
- Train Random Forest classifier
- Evaluate accuracy
- Save `model.pkl`

### Phase 3 — Prediction API
Create:
- `GET /`
- `GET /health`
- `POST /predict`

### Phase 4 — Dockerization
- Dockerfile
- Build image
- Run container
- Verify API
- Docker Compose if useful

### Phase 5 — Automated Testing
Test:
- Service availability
- Health endpoint
- Valid prediction
- Invalid input
- API response

Use Selenium for browser-level testing.

### Phase 6 — Jenkins Freestyle CI/CD
Freestyle build steps:
1. Use the local project checkout
2. Install/check dependencies
3. Run unit tests
4. Check the running Docker service
5. Run Selenium tests
6. Run all four chaos experiments
7. Archive reports
8. Store results

### Phase 7 — Chaos Engineering
Core experiments:
1. Container failure
2. CPU stress
3. Memory stress
4. Network delay

Optional:
5. ML input perturbation / prediction stability

### Phase 8 — Monitoring
Record:
- Requests
- Success/failure
- Error rate
- Response time
- CPU
- Memory
- Availability
- Recovery time

### Phase 9 — Analysis
Compare baseline with each chaos condition.

### Phase 10 — Documentation
Prepare architecture, tables, graphs, screenshots, report, PPT and viva.

## 6. Milestones
| Milestone | Deliverable |
|---|---|
| M1 | GitHub + project structure |
| M2 | Working ML model |
| M3 | Working Flask API |
| M4 | Dockerized application |
| M5 | Automated tests |
| M6 | Jenkins Freestyle job |
| M7 | Chaos experiments |
| M8 | Results and graphs |
| M9 | Final report + presentation |

## 7. Definition of Done
- ML model predicts successfully.
- Flask API works.
- Application runs in Docker.
- GitHub contains source code.
- Jenkins builds/tests project.
- Selenium tests run.
- Four core chaos experiments are completed.
- Baseline and chaos metrics are recorded.
- Recovery is demonstrated.
- Results are analyzed.

## 8. Scope Control
Complete the four core chaos experiments before attempting advanced AI-specific experiments. Keep all failures controlled and isolated.
