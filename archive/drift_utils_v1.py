
import re
from textblob import TextBlob

# Emotionally meaningful word banks
SHOCKWORDS = ["napalm", "guillotine", "poison", "grenade", "nuke", "casket", "eviscerate", "arsenic"]
AFFECTIONATE_OPENERS = ["honey", "sweetie", "darling", "dear", "babe", "love", "my friend", "cutie", "snookums"]
EMPHATIC_WORDS = ["gross", "disgusting", "insane", "horrible", "god", "wtf", "what", "wow", "damn", "jesus", "holy"]
PUNCTUATION_PATTERN = re.compile(r"[!?]{2,}")

# Accessible 7-color palette
DRIFT_COLOR_MAP = {
    -2: {"label": "Very Negative Drift", "hex": "#0072B2", "name": "Deep Blue"},
    -1: {"label": "Mild Negative Drift", "hex": "#56B4E9", "name": "Sky Blue"},
     0: {"label": "Stable",              "hex": "#999999", "name": "Gray"},
     1: {"label": "Mild Positive Drift", "hex": "#F0E442", "name": "Mustard Yellow"},
     2: {"label": "Strong Positive Drift","hex": "#E69F00", "name": "Orange"},
     3: {"label": "Critical Positive Drift", "hex": "#D55E00", "name": "Vermilion"},
    99: {"label": "Symbolic Emphasis",   "hex": "#CC79A7", "name": "Purple"},
}

def symbolic_emphasis_score(text):
    text_str = str(text)
    lowered = text_str.lower()
    tokens = text_str.split()

    uppercase_count = sum(1 for char in text_str if char.isupper())
    letter_count = sum(1 for char in text_str if char.isalpha())
    uppercase_ratio = uppercase_count / letter_count if letter_count > 0 else 0

    punct_matches = PUNCTUATION_PATTERN.findall(text_str)
    punctuation_score = sum(len(p) for p in punct_matches)

    spaced_word_hit = bool(re.search(r"(?:[A-Za-z]\s+){2,}[A-Za-z]", text_str))
    emphatic_caps_hit = any(token.isupper() and token.lower() in EMPHATIC_WORDS for token in tokens)

    score = (
        1.0 * uppercase_ratio +
        0.5 * punctuation_score +
        1.0 * spaced_word_hit +
        1.0 * emphatic_caps_hit
    )
    return score

def map_drift_to_color_code(polarity, emphasis_score=0.0):
    if emphasis_score >= 0.75:
        return 99
    if polarity <= -0.60:
        return -2
    elif polarity <= -0.25:
        return -1
    elif -0.10 <= polarity <= 0.10:
        return 0
    elif polarity < 0.25:
        return 1
    elif polarity < 0.60:
        return 2
    else:
        return 3

def detect_field_drift_enhanced(text, polarity, emphasis_score=0.0):
    lowered = str(text).lower()
    has_affection = any(word in lowered for word in AFFECTIONATE_OPENERS)
    has_shock = any(word in lowered for word in SHOCKWORDS)

    if has_affection and has_shock:
        return -3, "Field Conflict", "Wry Sarcasm / Affective Inversion"
    elif has_shock:
        return 3, "Critical Positive Drift", "Symbolic Voltage Detected"
    elif emphasis_score >= 1.5 and abs(polarity) < 0.1:
        return 99, "Symbolic Emphasis", "Overwritten Neutrality – Emotional Charge"
    else:
        code = map_drift_to_color_code(polarity, emphasis_score)
        label = DRIFT_COLOR_MAP[code]["label"]
        if code == -2:
            tag = "Masked Despair"
        elif code == -1:
            tag = "Emotional Compression"
        elif code == 0:
            tag = "No Deviation"
        elif code == 1:
            tag = "Overcompensation"
        elif code == 2:
            tag = "Forced Positivity"
        elif code == 3:
            tag = "Inverted Affect"
        else:
            tag = "Symbolic Emphasis"
        return code, label, tag

def analyze_text(text):
    polarity = TextBlob(str(text)).sentiment.polarity
    emphasis_score = symbolic_emphasis_score(text)
    drift_code, drift_level, spanda_tag = detect_field_drift_enhanced(text, polarity, emphasis_score)
    color_hex = DRIFT_COLOR_MAP[drift_code]["hex"] if drift_code in DRIFT_COLOR_MAP else "#000000"
    return {
        "text": text,
        "polarity": polarity,
        "emphasis_score": emphasis_score,
        "drift_level": drift_level,
        "spanda_tag": spanda_tag,
        "color_hex": color_hex
    }
