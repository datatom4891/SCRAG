from dataclasses import dataclass

@dataclass
class InjectionScanResult:
    initial_text: str
    normalized_text: str
    matched_rules: list[str]
    score: int
    decision: str

@dataclass
class SecurityCheckResult:
    failed_injection_check: bool
    injection_check_decision: str
    sanitized_text: str | None