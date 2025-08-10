import os
import sys
import pytest

# Ensure the project root is on the import path so ``utils`` can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.PriceBuffer import PriceBuffer


def _bar(ts, o=1, h=2, l=0, c=1):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": c}


def test_update_from_bar_respects_max_size():
    buf = PriceBuffer(maxBars=3)
    bars = [
        _bar("2024-01-01T00:00:00Z"),
        _bar("2024-01-01T00:01:00Z"),
        _bar("2024-01-01T00:02:00Z"),
        _bar("2024-01-01T00:03:00Z"),
    ]
    for b in bars:
        buf.updateFromBar(b)
    stored = buf.getBars()
    assert len(stored) == 3
    assert stored[0]["timestamp"] == "2024-01-01T00:01:00Z"
    assert stored[-1]["timestamp"] == "2024-01-01T00:03:00Z"


def test_update_from_bar_ignores_invalid_input():
    buf = PriceBuffer()
    buf.updateFromBar({"open": 1})
    assert buf.getBars() == []


def test_timestamp_normalization():
    buf = PriceBuffer()
    buf.updateFromBar(_bar("2024-01-01T00:00:00"))  # missing trailing Z
    stored = buf.getBars()
    assert stored[0]["timestamp"].endswith("Z")
