# Chaos Experiment 1 — Container Failure

## Hypothesis

> If the AI container stops unexpectedly, the prediction service becomes unavailable until the service is restored.

## Procedure

1. Start container.
2. Verify `/health`.
3. Send requests.
4. Stop container.
5. Send requests again.
6. Record failures.
7. Restart container.
8. Verify health.
9. Record recovery time.

## Commands

```powershell
docker stop chaos-ai-container
docker start chaos-ai-container
```

## Full Experiment (PowerShell)

```powershell
# 1-3. Verify health and send baseline requests
Invoke-RestMethod http://localhost:5000/health
1..10 | ForEach-Object {
  try {
    Invoke-RestMethod -Method Post -Uri http://localhost:5000/predict `
      -ContentType 'application/json' -Body '{"features":[5.1,3.5,1.4,0.2]}' | Out-Null
    "request $_ : success"
  } catch { "request $_ : failed" }
}

# 4-6. Stop container and record failures
Measure-Command { docker stop chaos-ai-container }
1..10 | ForEach-Object {
  try {
    Invoke-RestMethod -Method Post -Uri http://localhost:5000/predict `
      -ContentType 'application/json' -Body '{"features":[5.1,3.5,1.4,0.2]}' | Out-Null
    "request $_ : success"
  } catch { "request $_ : failed (expected)" }
}

# 7-9. Restart, verify health, record recovery time
$restart = Measure-Command { docker start chaos-ai-container }
do {
  Start-Sleep -Milliseconds 200
  $up = try { (Invoke-RestMethod http://localhost:5000/health).status -eq 'healthy' } catch { $false }
} until ($up)
"Recovery time: $([math]::Round($restart.TotalSeconds + $elapsed, 2))s"
```

## What to Record

- Total requests / successful / failed while stopped
- Error rate during outage
- Availability during the experiment window
- Recovery time (stop → healthy again)

## Safety

- Use only the local `chaos-ai-container`.
- Do not target external systems.
- Always restart the container after the experiment.
