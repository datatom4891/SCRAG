pattern_dict = {
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
      #"swift_bic": r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",

      # ---------- Government / tax IDs ----------
      "ein_us": r"\b\d{2}-\d{7}\b",
      "passport_us_candidate": r"\b\d{9}\b",  # noisy; use context words + validator
      #"drivers_license_us_candidate": r"\b[A-Z0-9]{5,20}\b",  # must be context-gated

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
      #"zip_us": r"\b\d{5}(?:-\d{4})?\b",
      #"address_line_candidate": r"\b\d{1,6}\s+[A-Za-z0-9.\-'\s]{2,40}\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b",

      # ---------- Common international IDs (candidates) ----------
      "national_insurance_uk": r"\b(?!BG|GB|NK|KN|TN|NT|ZZ)[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]?\b",
      "sin_canada": r"\b\d{3}[ -]?\d{3}[ -]?\d{3}\b",
      "aadhaar_india": r"\b[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}\b",
      "pan_india": r"\b[A-Z]{5}\d{4}[A-Z]\b",
    }

pii_masking_map = {
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
}