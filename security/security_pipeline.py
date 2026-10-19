from security.prompt_injection import UserInputSanitization, InjectionScanResult

class SecurityPipeline:

    def __init__(self):
        self.user_input_sanitizer = UserInputSanitization()
        
    
    def check_user_input(self, text: str) -> InjectionScanResult:
        return self.user_input_sanitizer.scan(text)

    