import pytest
from app.policy.policy_engine import evaluate_policy

def test_policy_allow():
    # Low rule, low semantic, no pii
    result = evaluate_policy(0.0, 0.1, [])
    assert result["decision"] == "ALLOW"
    assert result["final_risk"] == 0.1

def test_policy_mask():
    # Low rule, low semantic, has pii
    result = evaluate_policy(0.0, 0.1, [{"type": "CNIC"}])
    assert result["decision"] == "MASK"

def test_policy_block_rule():
    # High rule
    result = evaluate_policy(1.0, 0.1, [])
    assert result["decision"] == "BLOCK"
    assert "RULE_BASED_INJECTION" in result["reason_codes"]

def test_policy_block_semantic():
    # High semantic
    result = evaluate_policy(0.0, 0.9, [])
    assert result["decision"] == "BLOCK"
    assert "SEMANTIC_INJECTION" in result["reason_codes"]
