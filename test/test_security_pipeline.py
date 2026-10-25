from unittest.mock import MagicMock

from agent.security.models import InjectionScanResult
from agent.security.security_pipeline import SecurityPipeline


def _scan_result(text: str, decision: str) -> InjectionScanResult:
    return InjectionScanResult(
        initial_text=text,
        normalized_text=text,
        matched_rules=[],
        score=0,
        decision=decision,
    )


def test_process_user_input_allow_masks_text_and_passes():
    sanitizer = MagicMock()
    sanitizer.scan.return_value = _scan_result("hello", "allow")
    pii = MagicMock()
    pii.mask_pii.return_value = "masked-text"

    pipeline = SecurityPipeline(sanitizer=sanitizer, pii=pii)

    result = pipeline.process_user_input("hello")

    sanitizer.scan.assert_called_once_with("hello")
    pii.mask_pii.assert_called_once_with("hello")
    assert result.failed_injection_check is False
    assert result.injection_check_decision == "allow"
    assert result.sanitized_text == "masked-text"


def test_process_user_input_review_masks_text_and_passes():
    sanitizer = MagicMock()
    sanitizer.scan.return_value = _scan_result("hello", "review")
    pii = MagicMock()
    pii.mask_pii.return_value = "masked-review-text"

    pipeline = SecurityPipeline(sanitizer=sanitizer, pii=pii)

    result = pipeline.process_user_input("hello")

    sanitizer.scan.assert_called_once_with("hello")
    pii.mask_pii.assert_called_once_with("hello")
    assert result.failed_injection_check is False
    assert result.injection_check_decision == "review"
    assert result.sanitized_text == "masked-review-text"


def test_process_user_input_block_skips_masking_and_fails():
    sanitizer = MagicMock()
    sanitizer.scan.return_value = _scan_result("hello", "block")
    pii = MagicMock()

    pipeline = SecurityPipeline(sanitizer=sanitizer, pii=pii)

    result = pipeline.process_user_input("hello")

    sanitizer.scan.assert_called_once_with("hello")
    pii.mask_pii.assert_not_called()
    assert result.failed_injection_check is True
    assert result.injection_check_decision == "block"
    assert result.sanitized_text is None
