# Chaos Experiment 4 — Network Delay

## Hypothesis

> Increased network latency increases end-to-end prediction response time.

## Procedure

1. Measure normal response time.
2. Introduce controlled delay.
3. Send the same workload.
4. Record latency/errors.
5. Remove delay.
6. Verify normal behavior.

## How to Introduce Delay

### Option A — Application-level delay (simplest, no admin rights)

Add a controlled delay inside the Flask app (e.g. `time.sleep(0.2)` at the
start of `/predict`), restart the container, run the workload, then remove the
delay and restart again to verify recovery.

### Option B — Docker network delay (Linux only)

```bash
docker exec chaos-ai-container apt-get update && \
docker exec chaos-ai-container apt-get install -y iproute2
docker exec chaos-ai-container tc qdisc add dev eth0 root netem delay 200ms
```

Remove the delay:

```bash
docker exec chaos-ai-container tc qdisc del dev eth0 root netem
```

### Option C — Windows `netsh` (admin PowerShell, affects local traffic)

```powershell
# Add 200 ms latency
netsh interface ipv4 add filter name="chaos-delay" interface="Wi-Fi" protocol=TCP
# Remove it after the experiment
netsh interface ipv4 delete filter name="chaos-delay" interface="Wi-Fi" protocol=TCP
```

## Workload

Send the same fixed workload used for the baseline (e.g. 100 requests) and
record:

- Average response time (baseline vs. delayed)
- Failed requests / error rate
- Recovery after the delay is removed

## Example Measurement Script

```powershell
python -c "import requests,statistics,time
lat=[]
for _ in range(100):
    t=time.time()
    requests.post('http://localhost:5000/predict',json={'features':[5.1,3.5,1.4,0.2]},timeout=10)
    lat.append((time.time()-t)*1000)
print(f'avg={statistics.mean(lat):.1f}ms')"
```

## Safety

- Use only an isolated/local test environment.
- Do not target external systems.
- Remove the delay after recording results.
- Stop the experiment if the host becomes unstable.
