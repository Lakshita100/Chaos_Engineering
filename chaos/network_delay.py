"""Chaos Experiment 4 — Network Delay.

Hypothesis:
    Increased network latency increases end-to-end prediction response time.

Procedure:
    1. Measure normal response time.
    2. Introduce controlled delay (netem inside the container).
    3. Send the same workload.
    4. Record latency/errors.
    5. Remove delay.
    6. Verify normal behavior.

Requirements:
    - Container started with:  docker run -d -p 5000:5000 --cap-add NET_ADMIN --name chaos-ai-container chaos-ai
    - iproute2 inside container: docker exec chaos-ai-container apt-get install -y iproute2

Run directly:        python chaos/network_delay.py
Or via menu runner:  python chaos/run_experiments.py
"""

import argparse
import subprocess
import time

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
FIX_NET_ADMIN = (
    "Container lacks NET_ADMIN. Recreate it with:\n"
    "  docker rm -f chaos-ai-container\n"
    "  docker run -d -p 5000:5000 --cap-add NET_ADMIN --name chaos-ai-container chaos-ai\n"
    "  docker exec chaos-ai-container apt-get update && docker exec chaos-ai-container apt-get install -y iproute2"
)
FIX_IPROUTE = (
    "iproute2 missing inside container. Install it with:\n"
    "  docker exec chaos-ai-container apt-get update\n"
    "  docker exec chaos-ai-container apt-get install -y iproute2"
)


def _tc(container: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "exec", container, "tc", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def _ensure_ready(container: str):
    probe = _tc(container, "qdisc", "show", "dev", "eth0")
    output = probe.stdout + probe.stderr
    if probe.returncode == 0:
        return
    if "Operation not permitted" in output:
        raise SystemExit(FIX_NET_ADMIN)
    if "No such file" in output or "not found" in output:
        raise SystemExit(FIX_IPROUTE)
    raise SystemExit(f"tc probe failed: {output.strip()}")


def run(url: str = TARGET_URL, requests_count: int = 50,
        delay_ms: int = 200, container: str = CONTAINER):
    """Run the network delay experiment and return the results row."""
    _ensure_ready(container)

    print(f"[{now()}] Step 1: measuring normal response time")
    normal_lat, normal_fail = run_workload(url, requests_count)
    print(
        f"[{now()}] Normal: avg={mean(normal_lat):.1f}ms "
        f"failures={normal_fail}"
    )

    print(f"[{now()}] Step 2: adding {delay_ms}ms netem delay in {container}")
    added = _tc(container, "qdisc", "add", "dev", "eth0", "root", "netem",
                "delay", f"{delay_ms}ms")
    if added.returncode != 0:
        raise SystemExit(f"Failed to add delay: {added.stderr.strip()}")
    print(f"[{now()}] {added.stdout.strip()}")

    print(f"[{now()}] Step 3-4: sending workload with delay active")
    delayed_lat, delayed_fail = run_workload(url, requests_count)
    print(
        f"[{now()}] Delayed: avg={mean(delayed_lat):.1f}ms "
        f"failures={delayed_fail}"
    )

    print(f"[{now()}] Step 5: removing delay")
    removed = _tc(container, "qdisc", "del", "dev", "eth0", "root", "netem")
    if removed.returncode != 0:
        raise SystemExit(f"Failed to remove delay: {removed.stderr.strip()}")

    print(f"[{now()}] Step 6: verifying normal behavior")
    recovery_start = time.time()
    recovery_lat, recovery_fail = run_workload(url, max(10, requests_count // 5))
    recovery = time.time() - recovery_start
    print(
        f"[{now()}] Recovered: avg={mean(recovery_lat):.1f}ms "
        f"failures={recovery_fail}"
    )

    success = len(delayed_lat) - delayed_fail
    row = build_row(
        experiment="Network Delay",
        total=len(delayed_lat),
        success=success,
        failures=delayed_fail,
        avg_ms=mean(delayed_lat),
        recovery=f"<{max(1, round(recovery))}s",
        remarks=(
            f"{delay_ms}ms netem delay; normal {mean(normal_lat):.1f}ms -> "
            f"delayed {mean(delayed_lat):.1f}ms -> recovered "
            f"{mean(recovery_lat):.1f}ms"
        ),
    )
    print_row(row)
    save_result(row)
    return row


def main():
    parser = argparse.ArgumentParser(description="Network delay chaos experiment")
    parser.add_argument("--url", default=TARGET_URL)
    parser.add_argument("--delay", type=int, default=200, help="Delay in ms")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--container", default=CONTAINER)
    args = parser.parse_args()
    run(url=args.url, requests_count=args.requests,
        delay_ms=args.delay, container=args.container)


if __name__ == "__main__":
    main()
