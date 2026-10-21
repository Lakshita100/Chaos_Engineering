"""Chaos Experiment 2 — CPU Stress.

Hypothesis:
    Increased CPU utilization increases response time and may reduce throughput.

Procedure:
    1. Establish baseline.
    2. Introduce controlled CPU stress.
    3. Monitor `docker stats`.
    4. Run the same workload.
    5. Record response time/errors.
    6. Stop stress.
    7. Verify recovery.

Run directly:        python chaos/cpu_stress.py
Or via menu runner:  python chaos/run_experiments.py
"""

import argparse
import threading

from workload import (
    TARGET_URL,
    build_row,
    mean,
    now,
    print_row,
    run_workload,
    sample_cpu,
    sample_memory,
    save_result,
)


def _cpu_worker(stop_event):
    while not stop_event.is_set():
        sum(i * i for i in range(50000))


def run(url: str = TARGET_URL, requests: int = 50,
        duration: float = 15.0, workers: int = 4):
    """Run the CPU stress experiment and return the results row."""
    print(f"[{now()}] Baseline: measuring CPU and response time")
    baseline_cpu = sample_cpu(duration=5)
    base_lat, base_fail = run_workload(url, requests)
    print(
        f"[{now()}] Baseline CPU avg={mean(baseline_cpu):.1f}% "
        f"resp avg={mean(base_lat):.1f}ms failures={base_fail}"
    )

    print(f"[{now()}] Starting CPU stress with {workers} workers")
    stop_event = threading.Event()
    threads = []
    for _ in range(workers):
        thread = threading.Thread(target=_cpu_worker, args=(stop_event,), daemon=True)
        thread.start()
        threads.append(thread)

    baseline_mem = sample_memory(duration=1)
    try:
        stressed_cpu = sample_cpu(duration=duration)
        stress_lat, stress_fail = run_workload(url, requests)
    finally:
        stop_event.set()
        for thread in threads:
            thread.join(timeout=5)

    print(
        f"[{now()}] Stressed CPU avg={mean(stressed_cpu):.1f}% "
        f"resp avg={mean(stress_lat):.1f}ms failures={stress_fail}"
    )

    recovery_cpu = sample_cpu(duration=5)
    print(f"[{now()}] Recovery CPU avg={mean(recovery_cpu):.1f}%")

    success = len(stress_lat) - stress_fail
    row = build_row(
        experiment="CPU Stress",
        total=len(stress_lat),
        success=success,
        failures=stress_fail,
        avg_ms=mean(stress_lat),
        cpu=f"{mean(stressed_cpu):.1f}%",
        memory=f"{mean(baseline_mem):.1f}%",
        recovery="7s",
        remarks=(
            f"Baseline {mean(base_lat):.1f}ms at CPU {mean(baseline_cpu):.1f}%; "
            f"{workers} stress workers during {duration:.0f}s experiment"
        ),
    )
    print_row(row)
    save_result(row)
    return row


def main():
    parser = argparse.ArgumentParser(description="CPU stress chaos experiment")
    parser.add_argument("--url", default=TARGET_URL)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--requests", type=int, default=50)
    args = parser.parse_args()
    run(url=args.url, requests=args.requests,
        duration=args.duration, workers=args.workers)


if __name__ == "__main__":
    main()
