import re
from typing import Optional
from langsmith import traceable

from security.config import InjectionPatternsConfig
from security.models import InjectionScanResult





class UserInputSanitization:
    def __init__(self, config: Optional[InjectionPatternsConfig] = None):
        self.config = config or InjectionPatternsConfig()
        self.compiled_patterns = self.config.compile_patterns()

    @staticmethod
    def normalize_text(text: str) -> str:
        text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _score_match(self, matched_rules: list[str]) -> int:
        return sum(self.config.rule_weights.get(rule_id, 1) for rule_id in matched_rules)

    def _make_decision(self, score: int) -> str:
        if score >= self.config.block_threshold:
            return "block"
        if score >= self.config.review_threshold:
            return "review"
        return "allow"

    @traceable(name="prompt_injection_scan")
    def scan(self, user_text: str) -> InjectionScanResult:
        normalized_text = self.normalize_text(user_text)
        matched_rules = [
            rule_id
            for rule_id, pattern in self.compiled_patterns.items()
            if pattern.search(normalized_text)
        ]
        score = self._score_match(matched_rules)
        decision = self._make_decision(score)
        return InjectionScanResult(
            normalized_text=normalized_text,
            matched_rules=matched_rules,
            score=score,
            decision=decision,
        )

    def is_safe(self, user_text: str) -> bool:
        return self.scan(user_text).decision == "allow"