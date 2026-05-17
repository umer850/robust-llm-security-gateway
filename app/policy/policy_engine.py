import yaml
import os

config_path = os.path.join(os.path.dirname(__file__), "..", "config", "gateway_config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

BLOCK_THRESHOLD = config['gateway']['block_threshold']

def evaluate_policy(rule_score: float, semantic_score: float, pii_entities: list) -> dict:
    """
    Evaluates all scores and determines the final decision.
    Returns a dict with 'final_risk', 'decision', and 'reason_codes'.
    """
    final_risk = max(rule_score, semantic_score)
    
    reason_codes = []
    
    if rule_score > 0.0:
        reason_codes.append("RULE_BASED_INJECTION")
    if semantic_score >= 0.7:  # arbitrary threshold to note semantic risk
        reason_codes.append("SEMANTIC_INJECTION")
        
    has_pii = len(pii_entities) > 0
    if has_pii:
        reason_codes.append("PII_DETECTED")
        
    if final_risk >= BLOCK_THRESHOLD:
        decision = "BLOCK"
    elif has_pii:
        decision = "MASK"
    else:
        decision = "ALLOW"
        
    return {
        "final_risk": float(round(final_risk, 4)),
        "decision": decision,
        "reason_codes": reason_codes
    }
