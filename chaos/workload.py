"""Shared workload and result-recording helpers for chaos experiments.

Used by:
    container_failure.py, cpu_stress.py, memory_stress.py,
    network_delay.py, run_experiments.py
"""

import csv
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_CSV = PROJECT_ROOT / "results" / "experiment_results.csv"

COLUMNS = [
    "Experiment",
    "TotalRequests",
    "SuccessfulRequests",
    "FailedRequests",
    "ErrorRate",
    "AverageResponseTime",
    "CPUUsage",
    "MemoryUsage",
    "RecoveryTime",
    "Availability",
    "Remarks",
]

DEFAULT_FEATURES = [5.1, 3.5, 1.4, 0.2]
TARGET_URL = "http://localhost:5000"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def run_workload(url: str, count: int, features=None, timeout: int = 10):
    """Send a fixed workload of /predict requests.

    Returns (latencies_ms, failures).
    """
    features = features or DEFAULT_FEATURES
    latencies = []
    failures = 0
    for _ in range(count):
        start = time.time()
        try:
            response = requests.post(
                url + "/predict",
                json={"features": features},
                timeout=timeout,
            )
            if response.status_code != 200:
                failures += 1
        except requests.RequestException:
            failures += 1
        latencies.append((time.time() - start) * 1000)
    return latencies, failures


def sample_cpu(duration: float, interval: float = 0.5) -> list:
    samples = []
    deadline = time.time() + duration
    while time.time() < deadline:
        samples.append(psutil.cpu_percent(interval=interval))
    return samples or [psutil.cpu_percent()]


def sample_memory(duration: float, interval: float = 0.5) -> list:
    samples = []
    deadline = time.time() + duration
    while time.time() < deadline:
        samples.append(psutil.virtual_memory().percent)
        time.sleep(interval)
    return samples or [psutil.virtual_memory().percent]


def mean(samples) -> float:
    return statistics.mean(samples) if samples else 0.0


def build_row(experiment, total, success, failures, avg_ms,
              cpu="n/a", memory="n/a", recovery="0s", remarks=""):
    """Build one results row using the documented CSV columns."""
    err_rate = (failures / total * 100) if total else 0.0
    availability = (success / total * 100) if total else 0.0
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {
        "Experiment": experiment,
        "TotalRequests": total,
        "SuccessfulRequests": success,
        "FailedRequests": failures,
        "ErrorRate": f"{err_rate:.1f}%",
        "AverageResponseTime": f"{avg_ms:.1f}ms",
        "CPUUsage": cpu,
        "MemoryUsage": memory,
        "RecoveryTime": recovery,
        "Availability": f"{availability:.1f}%",
        "Remarks": f"{remarks} (measured {stamp})",
    }


def print_row(row):
    print("\n=== Result ===")
    for column in COLUMNS:
        print(f"{column}: {row[column]}")


def save_result(row):
    """Upsert the row into results/experiment_results.csv (by Experiment name)."""
    rows = []
    if RESULTS_CSV.exists() and RESULTS_CSV.stat().st_size > 0:
        with open(RESULTS_CSV, newline="", encoding="utf-8") as handle:
            rows = [
                existing
                for existing in csv.DictReader(handle)
                if existing.get("Experiment") != row["Experiment"]
            ]
    rows.append(row)

    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {RESULTS_CSV}")
