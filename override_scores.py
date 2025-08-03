OVERRIDE_WEIGHTS = {
    "symbolic_override": 100,
    "mocked_echo": 90,
    "rhetorical_drift": 85,
    "sarcasm_hint": 80,
    "negation_amplified": 75,
    "emphasis_override": 70,
    "stable_rationale": 65,
    "emoji_emphasis_override": 60,
} 

OVERRIDE_MESSAGES = {
    "mocked_echo": "Incoming mirrors baseline with elevated emphasis.",
    "rhetorical_drift": "Incoming uses rhetorical question form as a tone shift.",
    "sarcasm_hint": "Trailing or embedded sarcasm marker detected.",
    "negation_amplified": "Negation with shared root detected; drift amplified beyond polarity shift.",
    "emphasis_override": "Excessive emphasis detected (e.g., ALL CAPS or punctuation).",
    "stable_rationale": "Hedging phrase detected and drift within threshold.",
    "emoji_emphasis_override": "Emoji count triggered emphasis override — not considered drift.",
}