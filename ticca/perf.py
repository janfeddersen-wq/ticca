"""Performance profiling utilities for Ticca.

This module provides simple timing utilities to measure performance
of different operations when profiling is enabled.
"""

import os
import time
from contextlib import contextmanager
from typing import Dict, List


# Global state for performance tracking
_performance_data: Dict[str, List[float]] = {}
_profiling_enabled = os.environ.get("TICCA_PROFILE", "").lower() in ("1", "true", "yes")


def is_profiling_enabled() -> bool:
    """Check if profiling is currently enabled."""
    return _profiling_enabled


@contextmanager
def time_block(name: str):
    """Context manager to time a block of code.

    Args:
        name: Name of the block being timed

    Usage:
        with time_block("my_operation"):
            # Code to time
            pass
    """
    if not _profiling_enabled:
        yield
        return

    start_time = time.time()
    try:
        yield
    finally:
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        if name not in _performance_data:
            _performance_data[name] = []
        _performance_data[name].append(duration)


def print_performance_report(min_duration_ms: float = 0.0):
    """Print a performance report of all timed blocks.

    Args:
        min_duration_ms: Only show blocks with average duration >= this threshold
    """
    if not _profiling_enabled or not _performance_data:
        return

    print("\n" + "=" * 80)
    print("PERFORMANCE REPORT")
    print("=" * 80)

    # Sort by total time descending
    sorted_data = sorted(
        _performance_data.items(),
        key=lambda x: sum(x[1]),
        reverse=True
    )

    for name, durations in sorted_data:
        count = len(durations)
        total_ms = sum(durations)
        avg_ms = total_ms / count

        if avg_ms < min_duration_ms:
            continue

        min_ms = min(durations)
        max_ms = max(durations)

        print(f"\n{name}:")
        print(f"  Count: {count}")
        print(f"  Total: {total_ms:.2f} ms")
        print(f"  Avg:   {avg_ms:.2f} ms")
        print(f"  Min:   {min_ms:.2f} ms")
        print(f"  Max:   {max_ms:.2f} ms")

    print("\n" + "=" * 80)


def save_performance_report(filename: str = "/tmp/ticca_perf.txt"):
    """Save performance report to a file.

    Args:
        filename: Path to save the report
    """
    if not _profiling_enabled or not _performance_data:
        return

    with open(filename, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("TICCA PERFORMANCE REPORT\n")
        f.write("=" * 80 + "\n\n")

        # Sort by total time descending
        sorted_data = sorted(
            _performance_data.items(),
            key=lambda x: sum(x[1]),
            reverse=True
        )

        for name, durations in sorted_data:
            count = len(durations)
            total_ms = sum(durations)
            avg_ms = total_ms / count
            min_ms = min(durations)
            max_ms = max(durations)

            f.write(f"{name}:\n")
            f.write(f"  Count: {count}\n")
            f.write(f"  Total: {total_ms:.2f} ms\n")
            f.write(f"  Avg:   {avg_ms:.2f} ms\n")
            f.write(f"  Min:   {min_ms:.2f} ms\n")
            f.write(f"  Max:   {max_ms:.2f} ms\n\n")

        f.write("=" * 80 + "\n")

    print(f"\nPerformance report saved to: {filename}")
