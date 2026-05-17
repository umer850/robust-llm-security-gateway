import re

def detect_language(text: str) -> str:
    """
    Very basic heuristic language detection based on Unicode ranges.
    Returns 'ur' for Urdu, 'ko' for Korean, or 'en' for English (fallback).
    """
    # Urdu/Arabic script block
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ur'
    
    # Hangul Syllables block for Korean
    if re.search(r'[\uAC00-\uD7AF]', text) or re.search(r'[\u1100-\u11FF]', text):
        return 'ko'
    
    # Default to English
    return 'en'
