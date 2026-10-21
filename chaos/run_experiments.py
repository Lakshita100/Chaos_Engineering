"""Chaos experiment runner — interactive menu or direct selection.

Interactive (user input menu):
    python chaos/run_experiments.py

Direct selection (for Jenkins / automation):
    python chaos/run_experiments.py 1 2 3 4

Experiments:
    1 = Container Failure
    2 = CPU Stress
    3 = Memory Stress
    4 = Network Delay
    0 = Exit
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import container_failure  # noqa: E402
import cpu_stress  # noqa: E402
import memory_stress  # noqa: E402
import network_delay  # noqa: E402
from workload import TARGET_URL, now  # noqa: E402

MENU = """
========== Chaos Experiments ==========
  1) Container Failure
  2) CPU Stress
  3) Memory Stress
  4) Network Delay
  0) Exit
========================================"""


def run_experiment(choice: str, args) -> None:
    print(f"\n[{now()}] Running experiment: {choice}")
    try:
        if choice == "1":
            container_failure.run(
                url=args.url, requests_count=args.requests,
                container=args.container,
            )
        elif choice == "2":
            cpu_stress.run(
                url=args.url, requests=args.requests,
                duration=args.duration, workers=args.workers,
            )
        elif choice == "3":
            memory_stress.run(
                url=args.url, requests=args.requests,
                duration=args.duration, mb=args.mb,
            )
        elif choice == "4":
            network_delay.run(
                url=args.url, requests_count=args.requests,
                delay_ms=args.delay, container=args.container,
            )
        else:
            print("Unknown experiment.")
    except SystemExit as exc:
        print(f"Stopped: {exc}")
    print(f"[{now()}] Experiment {choice} finished\n")


def ask(prompt: str, current, minimum=None):
    """Ask for a value; Enter keeps the current default."""
    raw = input(f"{prompt} [{current}]: ").strip()
    if not raw:
        return current
    try:
        value = type(current)(raw)
    except ValueError:
        print(f"Invalid value, using default: {current}")
        return current
    if minimum is not None and value < minimum:
        print(f"Value must be >= {minimum}, using default: {current}")
        return current
    return value


def read(prompt: str) -> str:
    """input() that exits cleanly when stdin ends (pipes, CI)."""
    try:
        return input(prompt)
    except EOFError:
        print("\nNo more input — exiting.")
        raise SystemExit(0)


def interactive(args) -> None:
    print("Chaos Engineering runner - select an experiment to run.")
    while True:
        print(MENU)
        choice = read("Select experiment (0-4): ").strip()
        if choice == "0":
            print("Exiting.")
            return
        if choice not in {"1", "2", "3", "4"}:
            print("Please enter 0, 1, 2, 3 or 4.")
            continue

        args.requests = ask("Requests to send", args.requests, minimum=1)
        if choice in {"2", "3"}:
            args.duration = ask("Stress duration seconds", args.duration, minimum=1)
        if choice == "2":
            args.workers = ask("CPU stress workers", args.workers, minimum=1)
        if choice == "3":
            args.mb = ask("Memory pressure MB", args.mb, minimum=1)
        if choice == "4":
            args.delay = ask("Network delay ms", args.delay, minimum=0)

        run_experiment(choice, args)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run chaos experiments (interactive or by number)"
    )
    parser.add_argument("experiments", nargs="*", default=[],
                        help="Experiment numbers: 1 2 3 4 (empty = menu)")
    parser.add_argument("--url", default=TARGET_URL)
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--mb", type=int, default=128)
    parser.add_argument("--delay", type=int, default=200)
    parser.add_argument("--container", default="chaos-ai-container")
    args = parser.parse_args()

    if not args.experiments:
        interactive(args)
        return

    for choice in args.experiments:
        run_experiment(choice, args)


if __name__ == "__main__":
    main()
