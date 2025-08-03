from dataclasses import dataclass
from typing import Optional

@dataclass
class DriftResult:
    drift: bool
    label: str
    rationale: str
    field_responsiveness: str
    drift_score: Optional[float] = None
    emphasis_override: bool = False
    symbolic_override: bool = False
    mirror_match: bool = False