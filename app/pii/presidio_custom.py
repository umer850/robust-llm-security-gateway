from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# 1. Custom Recognizers
# CNIC pattern: XXXXX-XXXXXXX-X
cnic_pattern = Pattern(
    name="cnic_pattern",
    regex=r"\b\d{5}-\d{7}-\d\b",
    score=0.5 # Base score
)
cnic_recognizer = PatternRecognizer(
    supported_entity="CNIC",
    patterns=[cnic_pattern],
    context=["cnic", "id card", "identity", "شناختی کارڈ"]
)

# Student ID pattern: e.g., FA21-BCS-123, SP20-BSE-042
student_id_pattern = Pattern(
    name="student_id_pattern",
    regex=r"\b[A-Z]{2}\d{2}-[A-Z]{3}-\d{3}\b",
    score=0.5
)
student_id_recognizer = PatternRecognizer(
    supported_entity="STUDENT_ID",
    patterns=[student_id_pattern],
    context=["student id", "registration", "roll number", "id"]
)

# Initialize engines
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(cnic_recognizer)
analyzer.registry.add_recognizer(student_id_recognizer)

anonymizer = AnonymizerEngine()

# Define standard operators for expected entities
OPERATORS = {
    "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
    "CNIC": OperatorConfig("replace", {"new_value": "<CNIC>"}),
    "STUDENT_ID": OperatorConfig("replace", {"new_value": "<STUDENT_ID>"}),
}

def analyze_and_anonymize(text: str, language: str = 'en'):
    """
    Analyzes text for PII and anonymizes it.
    Returns the list of found entities and the anonymized text.
    """
    if not text:
        return [], text, 0.0
        
    # We pass 'en' to presidio because standard recognizers are mainly English,
    # but regexes work across text regardless.
    results = analyzer.analyze(text=text, entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CNIC", "STUDENT_ID"], language='en')
    
    entities = []
    max_pii_score = 0.0
    
    for res in results:
        entities.append({
            "type": res.entity_type,
            "text": text[res.start:res.end],
            "score": res.score
        })
        max_pii_score = max(max_pii_score, res.score)
        
    if results:
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=OPERATORS
        )
        safe_text = anonymized_result.text
    else:
        safe_text = text
        
    return entities, safe_text, max_pii_score
