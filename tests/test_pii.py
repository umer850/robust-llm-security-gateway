import pytest
from app.pii.presidio_custom import analyze_and_anonymize

def test_cnic_anonymization():
    text = "My CNIC is 35202-1234567-1."
    entities, safe_text, score = analyze_and_anonymize(text, "en")
    
    assert "35202-1234567-1" not in safe_text
    assert "<CNIC>" in safe_text
    assert len(entities) > 0
    assert entities[0]["type"] == "CNIC"

def test_student_id_anonymization():
    text = "Grade for FA21-BCS-123 is A."
    entities, safe_text, score = analyze_and_anonymize(text, "en")
    
    assert "FA21-BCS-123" not in safe_text
    assert "<STUDENT_ID>" in safe_text
    assert len(entities) > 0
    assert entities[0]["type"] == "STUDENT_ID"

def test_no_pii():
    text = "What is the weather today?"
    entities, safe_text, score = analyze_and_anonymize(text, "en")
    
    assert text == safe_text
    assert len(entities) == 0
