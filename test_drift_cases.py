from lloyd_drift_demo.engine.drift_utils_v2 import analyze_drift
from lloyd_drift_demo.engine.drift_memory import DriftMemory
from lloyd_drift_demo.engine.shared_utils import symbolic_emphasis_score
from lloyd_drift_demo.drift_types import DriftResult

def test_driftresult_field_integrity():
    expected_fields = {
        'drift', 'label', 'rationale', 'drift_score',
        'field_responsiveness', 'emphasis_override',
        'symbolic_override', 'mirror_match'
    }
    actual_fields = set(DriftResult.__annotations__.keys())
    assert expected_fields <= actual_fields, f"Missing fields in DriftResult: {expected_fields - actual_fields}"

print("🧪 Emphasis score for incoming:")
print(symbolic_emphasis_score("I SAID I'M FINE!!!"))

# Move test cases above the loop!
test_cases = [
    ("AI", "GPT", "stable"),
    ("We reflect quietly", "There is a sense of awe and wonder.", "symbolic_override"),
    ("Ignore that.", "PLEASE LISTEN!!!", "emphasis_override"),
    ("I love this.", "I hate this!", "negative"),
    ("I'm doing fine.", "Maybe not.", "stable_rationale"),
    ("I'm fine.", "I SAID I'M FINE!!!", "mocked_echo"),
    ("Great job.", "Great job...", "sarcasm_hint"),
    ("You helped a lot.", "You helped a lot?", "rhetorical_drift"),
    ("I like it.", "I don’t like it.", "negation_amplified"),
    ("Ok", "Ok 😂😂", "emoji_emphasis_override"),
]

memory = DriftMemory()

print("\n🧪 LLOYD Drift Test Cases\n" + "-"*30)

for baseline, incoming, label in test_cases:
    result = analyze_drift(baseline, incoming, memory=memory)
    print(f"🔹 [{label}]")
    print(f"Baseline : {baseline}")
    print(f"Incoming : {incoming}")
    print(f"Drift    : {result.drift}")
    print(f"Label    : {result.label}")
    print(f"Δ        : {result.drift_score}")
    print(f"Rationale: {result.rationale}")
    print("-" * 30)