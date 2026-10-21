"""Chaos Experiment 1 — Container Failure.

Hypothesis:
    If the AI container stops unexpectedly, the prediction service becomes
    unavailable until the service is restored.

Procedure:
    1. Start container.
    2. Verify /health.
    3. Send requests.
    4. Stop container.
    5. Send requests again.
    6. Record failures.
    7. Restart container.
    8. Verify health.
    9. Record recovery time.

Run directly:        python chaos/container_failure.py
Or via menu runner:  python chaos/run_experiments.py
"""

import argparse
import subprocess
import time

import requests

from workload import (
    TARGET_URL,
    build_row,
    mean,
    now,
    print_row,
    run_workload,
    save_result,
)

CONTAINER = "chaos-ai-container"


def _docker(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=120
    )


def _healthy(url: str) -> bool:
    try:
        return (
            requests.get(url + "/health", timeout=2).json().get("status")
            == "healthy"
        )
    except requests.RequestException:
        return False


def run(url: str = TARGET_URL, requests_count: int = 20,
        container: str = CONTAINER):
    """Run the container failure experiment and return the results row."""
    print(f"[{now()}] Step 1-3: verifying health and sending baseline requests")
    if not _healthy(url):
        raise SystemExit(f"Service at {url} is not healthy — start it first.")
    pre_lat, pre_fail = run_workload(url, requests_count)
    print(
        f"[{now()}] Baseline: {len(pre_lat) - pre_fail}/{len(pre_lat)} "
        f"success, avg={mean(pre_lat):.1f}ms"
    )

    print(f"[{now()}] Step 4: stopping container {container}")
    stop = _docker("stop", container)
    if stop.returncode != 0:
        raise SystemExit(f"docker stop failed: {stop.stderr.strip()}")

    print(f"[{now()}] Step 5-6: sending requests while service is down")
    outage_lat, outage_fail = run_workload(url, requests_count, timeout=5)
    print(
        f"[{now()}] Outage: {outage_fail}/{len(outage_lat)} requests failed "
        "(expected)"
    )

    print(f"[{now()}] Step 7: restarting container {container}")
    start_time = time.time()
    start = _docker("start", container)
    if start.returncode != 0:
        raise SystemExit(f"docker start failed: {start.stderr.strip()}")

    print(f"[{now()}] Step 8: waiting for health check")
    while not _healthy(url):
        if time.time() - start_time > 60:
            raise SystemExit("Service did not become healthy within 60s")
        time.sleep(0.25)
    recovery = time.time() - start_time
    print(f"[{now()}] Step 9: recovery time = {recovery:.2f}s")

    total = len(pre_lat) + len(outage_lat)
    success = (len(pre_lat) - pre_fail) + (len(outage_lat) - outage_fail)
    row = build_row(
        experiment="Container Failure",
        total=total,
        success=success,
        failures=outage_fail,
        avg_ms=mean(pre_lat),
        recovery=f"{recovery:.2f}s",
        remarks=(
            f"{outage_fail}/{len(outage_lat)} requests failed while container "
            f"stopped; healthy again after docker start"
        ),
    )
    print_row(row)
    save_result(row)
    return row


def main():
    parser = argparse.ArgumentParser(description="Container failure experiment")
    parser.add_argument("--url", default=TARGET_URL)
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--container", default=CONTAINER)
    args = parser.parse_args()
    run(url=args.url, requests_count=args.requests, container=args.container)


if __name__ == "__main__":
    main()
