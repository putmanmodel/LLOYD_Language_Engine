# engine/token_heatmap.py

import re
from typing import List, Dict

import string

def generate_token_heatmap(text: str) -> dict:
    from transformers import pipeline
    import nltk
    nltk.download("punkt", quiet=True)
    from nltk.tokenize import word_tokenize

    classifier = pipeline("sentiment-analysis")
    tokens = word_tokenize(text)

    scored_tokens = []
    for word in tokens:
        clean_word = word.strip(string.punctuation)
        score = 1.0 if clean_word.lower() in ["disgusting", "outrageous", "horrible"] else 0.3
        scored_tokens.append({"word": word, "score": round(score, 2)})

    return {"tokens": scored_tokens}