"""
src/guardrails.py
Security Guardrails for LLM Inputs and Outputs.
"""
import re
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize PII Detectors
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Common Prompt Injection patterns
INJECTION_PATTERNS = [
    r"(?i)ignore (all )?previous instructions",
    r"(?i)system prompt",
    r"(?i)you are now (dan|an unrestricted ai)",
    r"(?i)bypass (security|rules)",
]

def check_prompt_injection(user_input: str) -> bool:
    """Returns True if a prompt injection is detected."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input):
            return True
    return False

def redact_pii(text: str) -> str:
    """Finds and redacts PII (Names, Emails, IPs) from the LLM response."""
    # Analyze text for PII
    results = analyzer.analyze(text=text, language='en')
    # Anonymize (e.g., replace with <EMAIL_ADDRESS>)
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_text.text
