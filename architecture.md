# Chaos Engineering for AI Systems — Architecture

## 1. High-Level Architecture

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
        |                |
        | Flask API      |
        |      |         |
        |      v         |
        |   ML Model     |
        +-------+--------+
                |
                v
       Prediction / Health
                |
                v
       Monitoring & Metrics
                ^
                |
       Chaos Experiments
       /      |       |          CPU     Memory  Network  Container
   Stress   Stress   Delay    Failure
```

## 2. Application Flow

```text
Client
  |
  | HTTP request
  v
Flask API
  |
  +--> /health --> Health Status
  |
  +--> /predict --> Input Validation
                       |
                       v
                    ML Model
                       |
                       v
                   Prediction
```

## 3. CI/CD Flow

```text
Developer
   |
   | git push
   v
GitHub
   |
   v
Jenkins
   |
   +--> Checkout
   +--> Install Dependencies
   +--> Unit Tests
   +--> Build Docker Image
   +--> Start Container
   +--> Health Check
   +--> Selenium Tests
   +--> Chaos Experiments
   +--> Archive Results
```

## 4. Chaos Flow

```text
Running AI Container
        |
   +----+----+---------+
   |         |         |
   v         v         v
CPU Stress Memory    Network
             Stress    Delay
   |         |         |
   +---------+---------+
             |
             v
      Service Behaviour
             |
       +-----+------+
       |            |
       v            v
   Degradation   Recovery
```

Container failure:

```text
Running Container
       |
       v
Container stopped
       |
       v
Service unavailable
       |
       v
Container restarted
       |
       v
Health check passes
```

## 5. Metrics
- Response time
- Error rate
- Successful requests
- CPU usage
- Memory usage
- Availability
- Recovery time

## 6. Chaos Engineering Cycle

```text
Establish Baseline
       ↓
Form Hypothesis
       ↓
Introduce Controlled Failure
       ↓
Observe
       ↓
Measure Impact
       ↓
Recover
       ↓
Analyze
       ↓
Improve
```
