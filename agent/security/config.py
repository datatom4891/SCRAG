import re
from dataclasses import dataclass, field
from agent.security.regex_patterns.injection_patterns import pattern_dict as ip_patterns, injection_rule_weights
from agent.security.regex_patterns.pii_patterns import pattern_dict as pii_patterns, pii_masking_map


@dataclass
class InjectionPatternsConfig:
    injection_patterns: dict[str, str] = field(default_factory=lambda: ip_patterns)
    rule_weights: dict[str, int] = field(default_factory=lambda: injection_rule_weights)
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
    pii_patterns: dict[str, str] = field(default_factory=lambda: pii_patterns)
    
    pii_masks: dict[str, str] = field(default_factory= lambda: pii_masking_map)
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