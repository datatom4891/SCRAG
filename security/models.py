from dataclasses import dataclass

@dataclass
class InjectionScanResult:
    normalized_text: str
    matched_rules: list[str]
    score: int
    decision: str