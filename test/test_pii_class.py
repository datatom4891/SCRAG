from agent.security.config import PIIPatternsConfig
from agent.security.pii import MaskPIIInUserInput


def test_mask_pii_replaces_known_patterns_with_config_masks():
    config = PIIPatternsConfig(
        pii_patterns={
            "email": r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b",
            "ticket_id": r"\bTKT-\d{4}\b",
        },
        pii_masks={
            "email": "[EMAIL]",
            "ticket_id": "[TICKET ID]",
        },
    )
    masker = MaskPIIInUserInput(config=config)

    masked = masker.mask_pii("Email user@example.com about TKT-1234.")

    assert "[EMAIL]" in masked
    assert "[TICKET ID]" in masked
    assert "user@example.com" not in masked
    assert "TKT-1234" not in masked


def test_mask_pii_returns_original_text_when_no_patterns_match():
    config = PIIPatternsConfig(
        pii_patterns={"ticket_id": r"\bTKT-\d{4}\b"},
        pii_masks={"ticket_id": "[TICKET ID]"},
    )
    masker = MaskPIIInUserInput(config=config)
    text = "This sentence has no sensitive data."

    masked = masker.mask_pii(text)

    assert masked == text


def test_mask_pii_uses_unknown_placeholder_when_mask_missing():
    config = PIIPatternsConfig(
        pii_patterns={"custom_id": r"\bCUST-\d{4}\b"},
        pii_masks={},
    )
    masker = MaskPIIInUserInput(config=config)

    masked = masker.mask_pii("Reference CUST-1234 for this request.")

    assert masked == "Reference [UNKNOWN PII] for this request."
