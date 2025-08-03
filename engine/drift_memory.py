# lloyd_drift_demo/engine/drift_memory.py
from collections import deque

class DriftMemory:
    def __init__(self, max_len=5):
        self.history = deque(maxlen=max_len)

    def log(self, baseline: str, incoming: str, drift_score: float):
        self.history.append((baseline, incoming, drift_score))

    def recent_agitation(self, threshold: float = -0.5, window: int = 3) -> bool:
        """Detect if multiple recent entries were strongly negative."""
        recent = list(self.history)[-window:]
        return sum(1 for _, _, score in recent if score is not None and score < threshold) >= 2