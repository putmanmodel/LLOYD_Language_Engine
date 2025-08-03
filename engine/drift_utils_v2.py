from dataclasses import dataclass
from textblob import TextBlob
from typing import Optional, Dict, List, Union
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from ..drift_types import DriftResult
import emoji
import difflib
import inspect
from collections import deque

from lloyd_drift_demo.drift_types import DriftResult as DT
from .shared_utils import (
    get_polarity_score,
    detect_symbolic_override,
    is_rhetorical_drift,
    has_sarcasm_hint,
    DRIFT_THRESHOLD,
)
from ..override_scores import OVERRIDE_WEIGHTS, OVERRIDE_MESSAGES

# Verify imports
print("🧭 DriftResult in drift_utils_v2 ➔", DriftResult.__module__)
print("🧭 drift_types DriftResult ➔", DT.__module__)
assert DriftResult is DT, f"❌ DriftResult mismatch: {DriftResult} vs {DT}"

# ——————————————
# Config Loader
# ——————————————
DEFAULT_CONFIG = {
    "POLARITY_THRESHOLD": 0.15,
    "EMPHASIS_OVERRIDE": 1.0,
    "RARE_TAGS": ["lament", "awe", "reverence", "resignation"]
}

def load_config(path: str = "drift_config.json") -> dict:
    if Path(path).is_file():
        with open(path) as f:
            return json.load(f)
    return DEFAULT_CONFIG

config = load_config()
POLARITY_THRESHOLD = config["POLARITY_THRESHOLD"]
EMPHASIS_OVERRIDE = config["EMPHASIS_OVERRIDE"]
RARE_TAGS = set(config["RARE_TAGS"])
ACRONYM_WHITELIST = {"AI", "LLM", "GPT", "NASA", "CPU", "GPU", "URL", "PDF", "API", "SQL"}

# ——————————————
# Logging Setup
# ——————————————
logger = logging.getLogger("DriftUtils")
logger.setLevel(logging.INFO)

# ——————————————
# Text Normalization
# ——————————————
def normalize(text: str) -> str:
    return re.sub(r"[^\w\s']", "", text.lower()).strip()

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([!?])\1+", r"\1", text)
    text = re.sub(r"\b(\w)\s+\1\b", r"\1", text)
    return text.strip()

# ——————————————
# Symbolic Emphasis Score
# ——————————————
def symbolic_emphasis_score(text: str) -> float:
    caps = sum(1 for c in text if c.isupper())
    bangs = text.count("!")
    elongated = len([w for w in text.split() if any(c * 3 in w for c in w)])
    emoji_count = sum(1 for char in text if emoji.is_emoji(char))
    return (caps * 0.02) + (bangs * 0.1) + (elongated * 0.2) + (emoji_count * 0.1)

# ——————————————
# Symbolic Tag Stub
# ——————————————
def expand_symbolic_tags(text: str) -> Optional[str]:
    lowered = text.lower()
    for tag in RARE_TAGS:
        if tag in lowered:
            return "symbolic_" + tag
    return None

# ——————————————
# Token Heatmap Stub
# ——————————————
def attach_token_heatmap(text: str) -> Dict[str, List[Dict[str, Union[str, float]]]]:
    tokens = text.split()
    return {
        "tokens": [{"word": tok, "score": round(len(tok) / 10, 2)} for tok in tokens]
    }

# ——————————————
# Override Checks
# ——————————————
def is_mirrored(baseline: str, incoming: str) -> bool:
    return normalize(incoming).startswith(normalize(baseline)) or \
           difflib.SequenceMatcher(None, normalize(baseline), normalize(incoming)).ratio() > 0.85

def is_mocked_echo(baseline: str, incoming: str) -> bool:
    norm_b = normalize(baseline)
    norm_i = normalize(incoming)
    mirror_match = norm_b in norm_i or difflib.SequenceMatcher(None, norm_b, norm_i).ratio() > 0.65
    emphasis_b = symbolic_emphasis_score(baseline)
    emphasis_i = symbolic_emphasis_score(incoming)
    emphasis_delta = emphasis_i - emphasis_b
    print(f"[mocked_echo DEBUG] mirror_match={mirror_match}, Δemphasis={emphasis_delta:.2f}")
    return bool(mirror_match and emphasis_delta > 0.6)

def is_hedge_override(baseline: str, incoming: str) -> bool:
    hedge_terms = ["maybe", "perhaps", "i guess", "i think", "kind of", "sort of"]
    lowered = incoming.lower()
    return any(term in lowered for term in hedge_terms)

def is_emphasis_override(baseline: str, incoming: str) -> bool:
    emph = symbolic_emphasis_score(incoming)
    return emph >= EMPHASIS_OVERRIDE

def is_emoji_override(baseline: str, incoming: str) -> bool:
    count = sum(1 for char in incoming if emoji.is_emoji(char))
    return count >= 2

def is_negation_amplified(baseline: str, incoming: str) -> bool:
    negators = r"\b(not|don’t|never|no|nothing|can't|won't)\b"
    base_words = set(re.findall(r'\w+', baseline.lower()))
    incoming_words = set(re.findall(r'\w+', incoming.lower()))
    root_overlap = len(base_words & incoming_words) > 0
    return bool(re.search(negators, incoming.lower()) and root_overlap)

def compute_responsiveness(baseline: str, incoming: str, label: str) -> str:
    if label == "mocked_echo":
        return "reactive"
    if label in {"emphasis_override", "emoji_emphasis_override"}:
        if any(char.isupper() for char in incoming) and not is_mirrored(baseline, incoming):
            return "proactive"
    return "neutral"

# ——————————————
# Drift Memory
# ——————————————
drift_memory = deque(maxlen=5)

# ——————————————
# Drift Analysis Core
# ——————————————
def analyze_drift(baseline: str, incoming: str, memory=None) -> DriftResult:
    base_score = symbolic_emphasis_score(baseline)
    inc_score = symbolic_emphasis_score(incoming)
    drift_score = inc_score - base_score

    candidates = []

    if tag := detect_symbolic_override(incoming):
        candidates.append(("symbolic_override", OVERRIDE_WEIGHTS["symbolic_override"], f"Symbolic trigger: {tag}"))

    if is_mocked_echo(baseline, incoming):
        candidates.append(("mocked_echo", OVERRIDE_WEIGHTS["mocked_echo"], OVERRIDE_MESSAGES["mocked_echo"]))

    if is_rhetorical_drift(baseline, incoming):
        candidates.append(("rhetorical_drift", OVERRIDE_WEIGHTS["rhetorical_drift"], OVERRIDE_MESSAGES["rhetorical_drift"]))

    if has_sarcasm_hint(incoming) or incoming.strip().endswith("..."):
        candidates.append(("sarcasm_hint", OVERRIDE_WEIGHTS["sarcasm_hint"], OVERRIDE_MESSAGES["sarcasm_hint"]))

    if is_emphasis_override(baseline, incoming) and not is_mirrored(baseline, incoming):
        candidates.append(("emphasis_override", OVERRIDE_WEIGHTS["emphasis_override"], OVERRIDE_MESSAGES["emphasis_override"]))

    if is_hedge_override(baseline, incoming):
        candidates.append(("stable_rationale", OVERRIDE_WEIGHTS["stable_rationale"], OVERRIDE_MESSAGES["stable_rationale"]))

    if is_emoji_override(baseline, incoming):
        candidates.append(("emoji_emphasis_override", OVERRIDE_WEIGHTS["emoji_emphasis_override"], OVERRIDE_MESSAGES["emoji_emphasis_override"]))

    if is_negation_amplified(baseline, incoming):
        candidates.append(("negation_amplified", OVERRIDE_WEIGHTS["negation_amplified"], OVERRIDE_MESSAGES["negation_amplified"]))

    if candidates:
        label, score, rationale = max(candidates, key=lambda x: x[1])
        responsiveness = compute_responsiveness(baseline, incoming, label)
        return DriftResult(
            drift=(score >= 70),
            label=label,
            rationale=rationale,
            drift_score=drift_score,
            field_responsiveness=responsiveness,
        )

    if abs(drift_score) >= DRIFT_THRESHOLD:
        label = "positive" if drift_score > 0 else "negative"
        rationale = f"Polarity shift from {base_score} → {inc_score} (Δ={drift_score})"
        if memory and drift_score is not None:
            memory.log(baseline, incoming, drift_score)
            if label == "negative" and memory.recent_agitation():
                rationale += " (amplified by prior unresolved tension)"
        responsiveness = compute_responsiveness(baseline, incoming, label)
        return DriftResult(
            drift=True,
            label=label,
            rationale=rationale,
            drift_score=drift_score,
            field_responsiveness=responsiveness,
        )

    rationale = f"Polarity shift within tolerance (Δ={drift_score})"
    if memory and drift_score is not None:
        memory.log(baseline, incoming, drift_score)
    return DriftResult(
        drift=False,
        label="stable",
        rationale=rationale,
        drift_score=drift_score,
        field_responsiveness="neutral",
    )

# ——————————————
# Drift Journal Logger
# ——————————————
def log_drift_result(baseline: str, incoming: str, result: DriftResult, heatmap: dict, path: Optional[str] = None):
    if not path:
        return
    entry = {
        "timestamp": datetime.now().isoformat(),
        "baseline": baseline,
        "incoming": incoming,
        "result": {
            "label": result.label,
            "rationale": result.rationale,
            "drift_score": result.drift_score
        },
        "heatmap": heatmap
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")