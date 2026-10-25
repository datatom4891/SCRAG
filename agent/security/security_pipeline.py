from typing import Optional

from .prompt_injection import UserInputSanitization
from .pii import MaskPIIInUserInput
from .models import InjectionScanResult, SecurityCheckResult

class SecurityPipeline:

    def __init__(self, 
                 sanitizer: Optional[UserInputSanitization] = None,
                 pii: Optional[MaskPIIInUserInput] = None
                 ):
        self.user_input_sanitizer = sanitizer or UserInputSanitization()
        self.pii_checker = pii or MaskPIIInUserInput()
        
        
    
    def _injection_check(self, text: str) -> InjectionScanResult:
        return self.user_input_sanitizer.scan(text)
    
    def _mask_pii(self, text: str) -> str:
        return self.pii_checker.mask_pii(text)

    def process_user_input(self, text: str) -> SecurityCheckResult:
        
        injection_scan_result = self._injection_check(text)
        
        if injection_scan_result.decision == "allow":
            security_check_result = SecurityCheckResult(
                failed_injection_check= False,
                injection_check_decision= injection_scan_result.decision,
                sanitized_text = self._mask_pii(text)
            )
            return security_check_result
        elif injection_scan_result.decision == "review":
            security_check_result = SecurityCheckResult(
                failed_injection_check= False,
                injection_check_decision= injection_scan_result.decision,
                sanitized_text = self._mask_pii(text)
            )
            return security_check_result
        else:
            security_check_result = SecurityCheckResult(
                            failed_injection_check= True,
                            injection_check_decision= injection_scan_result.decision,
                            sanitized_text = None
                        )
            return security_check_result
        
        