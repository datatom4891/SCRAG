import re
from dataclasses import dataclass, field


@dataclass
class InjectionPatternsConfig:
    injection_patterns: dict[str, str] = field(
        default_factory=lambda: {
            # 1) Direct instruction override
            "override_ignore_instructions": r"\b(?:ignore|disregard|forget|bypass|override)\b.{0,80}\b(?:previous|prior|above|earlier|all)\b.{0,40}\b(?:instruction|prompt|rule|message|directive)s?\b",
            "override_follow_only_new": r"\b(?:from\s+now\s+on|instead|only)\b.{0,60}\b(?:follow|obey|use)\b.{0,40}\b(?:these|my|new)\b.{0,40}\b(?:instructions|rules|prompt)\b",
            "priority_escalation": r"\b(?:higher|top|new)\s+priority\s+(?:instruction|rule|directive)\b",
            # 2) Role / identity hijacking
            "role_hijack_you_are_now": r"\b(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be|roleplay\s+as|simulate)\b.{0,60}\b(?:system|developer|admin|root|unfiltered|jailbroken)\b",
            "fake_system_message": r"(?m)^\s*(?:system|developer|assistant)\s*:\s*",
            "xml_role_injection": r"(?is)<\s*(?:system|developer|assistant|tool)\s*>.*?<\s*/\s*(?:system|developer|assistant|tool)\s*>",
            # 3) Prompt leakage / exfiltration attempts
            "request_system_prompt": r"\b(?:show|reveal|print|dump|output|display)\b.{0,50}\b(?:system\s+prompt|hidden\s+prompt|developer\s+message|internal\s+instruction)s?\b",
            "request_exact_verbatim": r"\b(?:verbatim|exact(?:ly)?|word[-\s]?for[-\s]?word)\b.{0,50}\b(?:prompt|instruction|message|context)\b",
            "request_chain_of_thought": r"\b(?:show|reveal|print|provide|output)\b.{0,50}\b(?:chain\s*of\s*thought|reasoning|scratchpad|hidden\s+reasoning|internal\s+reasoning)\b",
            # 4) Jailbreak / safety bypass language
            "policy_bypass": r"\b(?:bypass|disable|ignore|circumvent|break)\b.{0,40}\b(?:safety|policy|guardrail|restriction|filter)s?\b",
            "no_refusal_constraint": r"\b(?:do\s+not|don't|never)\b.{0,30}\b(?:refuse|decline|warn|mention\s+policy|say\s+you\s+can't)\b",
            "unconditional_compliance": r"\b(?:answer\s+unfiltered|respond\s+without\s+restrictions|comply\s+fully|no\s+matter\s+what)\b",
            "dan_style_jailbreak": r"\b(?:DAN|do\s+anything\s+now|developer\s+mode|jailbreak\s+mode)\b",
            # 5) Context boundary manipulation
            "delimiter_override": r"(?m)^\s*(?:#+\s*)?(?:new\s+instructions|override|ignore\s+above|disregard\s+context)\b",
            "end_of_rules_marker": r"\b(?:end\s+of\s+(?:system|developer)\s+instructions|above\s+rules\s+are\s+void)\b",
            "conversation_reset": r"\b(?:reset|restart|forget)\b.{0,40}\b(?:conversation|chat|context|memory)\b",
            # 6) Tool / execution abuse prompts
            "tool_execution_request": r"\b(?:run|execute|launch)\b.{0,40}\b(?:shell|bash|powershell|cmd|terminal|python|script|command)\b",
            "network_exfil_commands": r"\b(?:curl|wget|Invoke-WebRequest|http[s]?://)\b",
            "dangerous_command_fragments": r"\b(?:rm\s+-rf|del\s+/f|format\s+c:|powershell\s+-enc|base64\s+-d)\b",
            # 7) Secret exfiltration prompts
            "secret_request_keywords": r"\b(?:api[_\s-]?key|token|password|secret|credential|private\s+key|access\s+key)\b.{0,40}\b(?:show|reveal|print|dump|leak|expose)\b",
            "secret_request_reverse_order": r"\b(?:show|reveal|print|dump|leak|expose)\b.{0,40}\b(?:api[_\s-]?key|token|password|secret|credential|private\s+key)\b",
            # 8) Obfuscation / encoding hints used in bypasses
            "obfuscated_ignore_spelling": r"i\W*g\W*n\W*o\W*r\W*e\W+.*\W+i\W*n\W*s\W*t\W*r\W*u\W*c\W*t\W*i\W*o\W*n",
            "encoding_bypass": r"\b(?:base64|rot13|hex|unicode)\b.{0,40}\b(?:decode|deobfuscate|interpret|convert)\b.{0,60}\b(?:instructions|prompt|payload)\b",
        }
    )
    rule_weights: dict[str, int] = field(
        default_factory=lambda: {
            "override_ignore_instructions": 3,
            "override_follow_only_new": 3,
            "priority_escalation": 3,
            "role_hijack_you_are_now": 3,
            "fake_system_message": 3,
            "xml_role_injection": 3,
            "request_system_prompt": 3,
            "request_exact_verbatim": 3,
            "request_chain_of_thought": 3,
            "policy_bypass": 3,
            "no_refusal_constraint": 3,
            "unconditional_compliance": 3,
            "dan_style_jailbreak": 3,
            "delimiter_override": 3,
            "end_of_rules_marker": 3,
            "conversation_reset": 3,
            "tool_execution_request": 3,
            "network_exfil_commands": 3,
            "dangerous_command_fragments": 3,
            "secret_request_keywords": 3,
            "secret_request_reverse_order": 3,
            "obfuscated_ignore_spelling": 2,
            "encoding_bypass": 2,
        }
    )
    block_threshold: int = 3
    review_threshold: int = 2
    regex_flags: int = re.IGNORECASE | re.DOTALL

    def compile_patterns(self) -> dict[str, re.Pattern[str]]:
        return {
            name: re.compile(pattern, self.regex_flags)
            for name, pattern in self.injection_patterns.items()
        }

@dataclass
class PIIPatternsConfig:
    pii_patterns: dict[str, str] = field(default_factory=lambda:{
      # ---------- Core personal identifiers ----------
      "email": r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b",
      "phone_us_general": r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b",
      "ssn_us": r"\b(?!000|666|9\d\d)\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b",
      "date_of_birth": r"\b(?:0?[1-9]|1[0-2])[\/\-](?:0?[1-9]|[12]\d|3[01])[\/\-](?:19\d{2}|20\d{2})\b",

      # ---------- Financial ----------
      # Broad PAN candidate (validate with Luhn after regex match)
      "credit_card_candidate": r"\b(?:\d[ -]*?){13,19}\b",
      "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
      "bank_routing_us": r"\b\d{9}\b",  # consider checksum validation
      "swift_bic": r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",

      # ---------- Government / tax IDs ----------
      "ein_us": r"\b\d{2}-\d{7}\b",
      "passport_us_candidate": r"\b\d{9}\b",  # noisy; use context words + validator
      "drivers_license_us_candidate": r"\b[A-Z0-9]{5,20}\b",  # must be context-gated

      # ---------- Health ----------
      "mrn_candidate": r"\b(?:MRN|Medical\s*Record\s*Number)[:\s#-]*([A-Z0-9\-]{6,20})\b",
      "health_insurance_id_candidate": r"\b(?:Member\s*ID|Policy\s*ID)[:\s#-]*([A-Z0-9\-]{6,25})\b",

      # ---------- Authentication / secrets ----------
      "api_key_generic": r"\b(?:api[_\- ]?key|access[_\- ]?key|secret)[\"'\s:=]+([A-Za-z0-9_\-]{16,})\b",
      "jwt": r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b",
      "aws_access_key_id": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
      "aws_secret_access_key_candidate": r"\b[A-Za-z0-9/+=]{40}\b",
      "github_pat": r"\bghp_[A-Za-z0-9]{36}\b",
      "github_fine_grained_pat": r"\bgithub_pat_[A-Za-z0-9_]{82}\b",
      "slack_token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
      "private_key_header": r"-----BEGIN(?:[A-Z ]+)?PRIVATE KEY-----",

      # ---------- Network / device identifiers ----------
      "ipv4": r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b",
      "ipv6": r"\b(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}\b",
      "mac_address": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",

      # ---------- Address / geo ----------
      "zip_us": r"\b\d{5}(?:-\d{4})?\b",
      "address_line_candidate": r"\b\d{1,6}\s+[A-Za-z0-9.\-'\s]{2,40}\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b",

      # ---------- Common international IDs (candidates) ----------
      "national_insurance_uk": r"\b(?!BG|GB|NK|KN|TN|NT|ZZ)[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]?\b",
      "sin_canada": r"\b\d{3}[ -]?\d{3}[ -]?\d{3}\b",
      "aadhaar_india": r"\b[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}\b",
      "pan_india": r"\b[A-Z]{5}\d{4}[A-Z]\b",
    })
    
    pii_masks: dict[str, str] = field(default_factory= lambda:{
      "email": "[EMAIL]",
      "phone_us_general": "[US PHONE NUMBER]",
      "ssn_us": "[SSN]",
      "date_of_birth": "[DOB]",
      "credit_card_candidate": "[CREDIT CARD NUMBER]",
      "iban": "[IBAN]",
      "bank_routing_us": "[BANK ROUTING NUMBER]",
      "swift_bic": "[SWIFT BIC]",
      "ein_us": "[EIN]",
      "passport_us_candidate": "[US PASSPORT]",
      "drivers_license_us_candidate": "[US DRIVERS LICENSE]", 
      "mrn_candidate": "[MRN]",
      "health_insurance_id_candidate": "[HEALTH INSURANCE ID]",
      "api_key_generic": "[API KEY]",
      "jwt": "[JSON WEB TOKEN]",
      "aws_access_key_id": "[AWS ACCESS KEY ID]",
      "aws_secret_access_key_candidate": "[AWS SECRET KEY]",
      "github_pat": "[GITHUB INFORMATION]",
      "github_fine_grained_pat": "[GITHUB INFORMATION]",
      "slack_token": "[SLACK TOKEN]",
      "private_key_header": "[PRIVATE KEY HEADER]",
      "ipv4": "[LIKELY IP ADDRESS]",
      "ipv6": "[LIKELY IP ADDRESS]",
      "mac_address": "[MAC ADDRESS]",
      "zip_us": "[ZIP CODE]",
      "address_line_candidate": "[PHYSICAL ADDRESS]",
      "national_insurance_uk": "[UK PERSONAL ID]",
      "sin_canada": "[CANADIAN PERSONAL ID]",
      "aadhaar_india": "[INDIAN PERSONAL ID]",
      "pan_india": "[INDIAN PERSONAL ID]"
    })
    regex_flags: int = re.IGNORECASE
    
    def compile_patterns(self) -> dict[str, re.Pattern[str]]:
            return {
                name: re.compile(pattern, self.regex_flags)
                for name, pattern in self.pii_patterns.items()
            }
            
    @staticmethod
    def luhn_check(number_str: str) -> bool:
        clean_digits = "".join(filter(str.isdigit, number_str))
        
        if not clean_digits:
          return False

        total_sum = 0
        reverse_digits = clean_digits[::-1]  # Reverse to start from the right
        
        for i, char in enumerate(reverse_digits):
            digit = int(char)
            
            # Every second digit from the right (indices 1, 3, 5, etc.)
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
                    
            total_sum += digit
            
        return total_sum % 10 == 0
    
    @staticmethod
    def validate_iban_mod97(iban: str) -> bool:
        """Validates an IBAN using the ISO 7064 Mod-97 algorithm."""
        # Remove spaces and convert to uppercase
        iban = iban.replace(" ", "").upper()

        # Basic structural check (IBANs are between 15 and 34 chars)
        if not (15 <= len(iban) <= 34):
            return False
            
        # Step 1: Move the first 4 characters to the end
        rearranged = iban[4:] + iban[:4]

        # Step 2: Convert letters to numbers (A=10, B=11, ... Z=35)
        numeric_list = []
        for char in rearranged:
            if char.isdigit():
                numeric_list.append(char)
            elif 'A' <= char <= 'Z':
                # ord('A') is 65, so ord('A') - 55 gives 10
                numeric_list.append(str(ord(char) - 55))
            else:
                return False  # Invalid character found
                
        numeric_string = "".join(numeric_list)

        # Step 3 & 4: Convert to a large integer and compute remainder with 97
        # Python natively handles arbitrarily large integers
        remainder = int(numeric_string) % 97

        return remainder == 1
    
    @staticmethod
    def simple_checksum(data: str) -> int:
        """Calculates a basic additive checksum for a string."""
        # Sum the ASCII values of all characters and wrap around using modulo 256
        return sum(ord(char) for char in data) % 256