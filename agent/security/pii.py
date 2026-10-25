from typing import Optional
from langsmith import traceable

from .config import PIIPatternsConfig

class MaskPIIInUserInput:
    def __init__(self, config: Optional[PIIPatternsConfig] = None):
        self.config = config or PIIPatternsConfig()
        self.compiled_patterns = self.config.compile_patterns()
        self.masking_map = self.config.pii_masks
    
    @traceable(name="pii_scan")
    def mask_pii(self, text: str) -> str:
        masked_text = text
        for rule_id, pattern in self.compiled_patterns.items():
            pii_mask = self.masking_map.get(rule_id, "[UNKNOWN PII]")
            masked_text = pattern.sub(pii_mask, masked_text)
        
        return masked_text
