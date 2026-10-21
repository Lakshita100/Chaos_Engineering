"""Chaos Experiment 3 — Memory Stress.

Hypothesis:
    Increased memory pressure may cause performance degradation or service failure.

Procedure:
    1. Establish baseline.
    2. Introduce controlled memory stress.
    3. Monitor memory.
    4. Run workload.
    5. Record metrics.
    6. Remove stress.
    7. Verify recovery.

Never intentionally exhaust the host system's memory — the safety guard
refuses allocations that exceed half of the currently available RAM.

Run directly:        python chaos/memory_stress.py
Or via menu runner:  python chaos/run_experiments.py
"""

import argparse
import time

import psutil

from workload import (
    TARGET_URL,
    build_row,
    mean,
    now,
    print_row,
    run_workload,
    sample_memory,
    save_result,
)


def _allocate_memory(mb: int):
    return [bytearray(1024 * 1024) for _ in range(mb)]


def run(url: str = TARGET_URL, requests: int = 50,
        duration: float = 15.0, mb: int = 128):
    """Run the memory stress experiment and return the results row."""
    available_mb = psutil.virtual_memory().available // (1024 * 1024)
    if mb > available_mb // 2:
        raise SystemExit(
            f"Refusing to allocate {mb}MB: only {available_mb}MB available. "
            "Never intentionally exhaust host memory."
        )

    print(f"[{now()}] Baseline: measuring memory and response time")
    baseline_mem = sample_memory(duration=5)
    base_lat, base_fail = run_workload(url, requests)
    print(
        f"[{now()}] Baseline memory avg={mean(baseline_mem):.1f}% "
        f"resp avg={mean(base_lat):.1f}ms failures={base_fail}"
    )

    print(f"[{now()}] Allocating {mb}MB of memory pressure")
    block = _allocate_memory(mb)
    try:
        stressed_mem = sample_memory(duration=duration)
        stress_lat, stress_fail = run_workload(url, requests)
    finally:
        del block

    print(
        f"[{now()}] Stressed memory avg={mean(stressed_mem):.1f}% "
        f"resp avg={mean(stress_lat):.1f}ms failures={stress_fail}"
    )

    time.sleep(2)
    recovery_mem = sample_memory(duration=5)
    print(f"[{now()}] Recovery memory avg={mean(recovery_mem):.1f}%")

    success = len(stress_lat) - stress_fail
    row = build_row(
        experiment="Memory Stress",
        total=len(stress_lat),
        success=success,
        failures=stress_fail,
        avg_ms=mean(stress_lat),
        memory=f"{mean(stressed_mem):.1f}%",
        recovery="2s",
        remarks=(
            f"Baseline {mean(base_lat):.1f}ms at mem {mean(baseline_mem):.1f}%; "
            f"controlled {mb}MB pressure"
        ),
    )
    print_row(row)
    save_result(row)
    return row


def main():
    parser = argparse.ArgumentParser(description="Memory stress chaos experiment")
    parser.add_argument("--url", default=TARGET_URL)
    parser.add_argument("--mb", type=int, default=128,
                        help="Megabytes of memory to allocate (keep controlled)")
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--requests", type=int, default=50)
    args = parser.parse_args()
    run(url=args.url, requests=args.requests,
        duration=args.duration, mb=args.mb)


if __name__ == "__main__":
    main()
