# test_drift_utils_v2.py

import pytest
from drift_utils_v2 import analyze_drift, DriftResult
from unittest.mock import patch
import time

# ——————————————
# Parametrized Tests
# ——————————————
@pytest.mark.parametrize("baseline,incoming,expected_label", [
    ("I feel okay.", "I feel okay.", "stable"),
    ("This is fine.", "This is incredible!", "positive"),
    ("That was nice.", "That was awful.", "negative"),
])
def test_drift_basic(baseline, incoming, expected_label):
    result = analyze_drift(baseline, incoming)
    assert isinstance(result, DriftResult)
    assert result.label == expected_label

# ——————————————
# Emphasis Override Test
# ——————————————
def test_emphasis_override():
    result = analyze_drift("This is okay.", "I ABSOLUTELY LOVE IT!!!")
    assert result.label == "emphasis_override"
    assert result.drift is False

# ——————————————
# Symbolic Override (using patch)
# ——————————————
@patch("drift_utils_v2.expand_symbolic_tags")
def test_symbolic_override(mock_tags):
    mock_tags.return_value = "symbolic_lament"
    result = analyze_drift("Fine", "Deep lament overtook him.")
    assert result.label == "symbolic_override"
    assert result.drift is True
    assert result.rationale

# ——————————————
# Polarity Threshold Sensitivity
# ——————————————
def test_threshold_boundary():
    base = "It was fine."
    low_drift = "It was okay."      # Should be stable
    high_drift = "It was horrible." # Should trigger drift
    r1 = analyze_drift(base, low_drift)
    r2 = analyze_drift(base, high_drift)
    assert r1.drift is False
    assert r2.drift is True
    assert r2.label == "negative"

# ——————————————
# Smoke Test Performance
# ——————————————
def test_drift_speed():
    base = "This is fine."
    inc = "This is not fine."
    start = time.time()
    for _ in range(1000):
        analyze_drift(base, inc)
    elapsed = time.time() - start
    assert elapsed < 2.5