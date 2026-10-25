pattern_dict = {
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

injection_rule_weights = {
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