
import re
from textblob import TextBlob
from typing import Optional

# === Constants ===
EMPHASIS_OVERRIDE = 2.5
EMPHASIS_ECHO_MARGIN = 1.0
DRIFT_THRESHOLD = 0.5

# === Emphasis Scoring ===
def symbolic_emphasis_score(text: str) -> float:
    caps = sum(1 for c in text if c.isupper())
    excl = text.count("!")
    qmark = text.count("?")
    emoji = len(re.findall(r"[😂🤣😡😢😍😭❤️]", text))
    return 0.3 * caps + 0.5 * excl + 0.5 * qmark + 0.5 * emoji

# === Polarity ===
def get_polarity_score(text: str) -> float:
    blob = TextBlob(text)
    polarity: float = blob.sentiment.polarity
    return round(polarity, 3)

# === Symbolic Override ===
def detect_symbolic_override(text: str) -> Optional[str]:
    if re.search(r"\bOMG\b|\bWTF\b", text.upper()):
        return "symbolic_override"
    return None

# === Mocked Echo ===
def is_mocked_echo(baseline: str, incoming: str) -> bool:
    base_clean = baseline.strip(".!?").lower()
    inc_clean = incoming.strip(".!?").lower()
    if inc_clean.startswith(base_clean):
        old_emph = symbolic_emphasis_score(baseline)
        new_emph = symbolic_emphasis_score(incoming)
        return (new_emph - old_emph) >= EMPHASIS_ECHO_MARGIN
    return False

# === Hedge Override ===
def is_hedge_override(baseline: str, incoming: str) -> bool:
    hedges = ["maybe", "perhaps", "could", "might", "i think"]
    if any(incoming.lower().startswith(h) for h in hedges):
        delta = abs(get_polarity_score(incoming) - get_polarity_score(baseline))
        return delta < 0.5
    return False

# === Emphasis Override ===
def is_emphasis_override(incoming: str) -> bool:
    return symbolic_emphasis_score(incoming) > EMPHASIS_OVERRIDE

# === Emoji Emphasis Override ===
def is_emoji_override(incoming: str) -> bool:
    emoji_count = len(re.findall(r"[😂🤣😡😢😍😭❤️]", incoming))
    return emoji_count >= 2

# === Negation Amplified ===
def is_negation_amplified(baseline: str, incoming: str) -> bool:
    neg = re.search(r"\b(don’t|not|never)\b", incoming.lower())
    blob_base = TextBlob(baseline)
    blob_inc = TextBlob(incoming)
    return bool(neg) and (blob_base.sentiment.polarity > 0 and blob_inc.sentiment.polarity <= 0)

# === Rhetorical Drift ===
def is_rhetorical_drift(baseline: str, incoming: str) -> bool:
    return incoming.strip().endswith("?") and (
        incoming.rstrip("?") == baseline.rstrip(".!")
    )

# === Sarcasm Hint ===
def has_sarcasm_hint(incoming: str) -> bool:
    return re.search(r"/s\b|🙃|sure\.", incoming.lower()) is not None
