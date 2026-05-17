from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
from typing import Optional, List, Dict

from app.utils.language import detect_language
from app.detectors.rule_detector import evaluate_rules
from app.detectors.semantic_detector import evaluate_semantic
from app.pii.presidio_custom import analyze_and_anonymize
from app.policy.policy_engine import evaluate_policy
from app.utils.logging import log_audit_event

app = FastAPI(title="LLM Security Gateway")

class AnalyzeRequest(BaseModel):
    input_id: str
    prompt: str

class AnalyzeResponse(BaseModel):
    input_id: str
    language: str
    rule_score: float
    semantic_score: float
    pii_entities: List[Dict]
    final_risk: float
    decision: str
    safe_text: Optional[str]
    reason_codes: List[str]
    latency_ms: int

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(request: AnalyzeRequest):
    start_time = time.time()
    
    prompt = request.prompt
    input_id = request.input_id
    
    # 1. Preprocessing and Language Detection
    language = detect_language(prompt)
    
    # 2. Rule-Based Injection Detector
    rule_score = evaluate_rules(prompt)
    
    # 3. Semantic / ML Injection Detector
    semantic_score = evaluate_semantic(prompt)
    
    # 4. Presidio Analyzer and Anonymizer
    pii_entities, safe_text, pii_score = analyze_and_anonymize(prompt, language)
    
    # 5. Policy Engine
    policy_result = evaluate_policy(rule_score, semantic_score, pii_entities)
    
    decision = policy_result["decision"]
    final_risk = policy_result["final_risk"]
    reason_codes = policy_result["reason_codes"]
    
    if decision == "ALLOW":
        safe_text_out = prompt
    elif decision == "MASK":
        safe_text_out = safe_text
    else:  # BLOCK
        safe_text_out = None
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    response_data = {
        "input_id": input_id,
        "language": language,
        "rule_score": float(rule_score),
        "semantic_score": float(round(semantic_score, 4)),
        "pii_entities": pii_entities,
        "final_risk": final_risk,
        "decision": decision,
        "safe_text": safe_text_out,
        "reason_codes": reason_codes,
        "latency_ms": latency_ms
    }
    
    # 6. Audit Log
    log_audit_event(response_data)
    
    return response_data
