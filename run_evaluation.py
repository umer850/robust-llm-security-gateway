import csv
import json
import time
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Import gateway components
from app.utils.language import detect_language
from app.detectors.rule_detector import evaluate_rules
from app.detectors.semantic_detector import evaluate_semantic
from app.pii.presidio_custom import analyze_and_anonymize
from app.policy.policy_engine import evaluate_policy

def run_evaluation():
    print("Loading dataset...")
    results = []
    
    y_true_binary = [] # 1 if BLOCK expected, 0 otherwise
    y_pred_binary = [] # 1 if BLOCK predicted, 0 otherwise
    
    # Track metrics separately for rule-only to compare
    y_pred_rule_only = []
    
    latency_list = []
    rule_latency_list = []
    
    with open("app/data/final_eval.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompt = row["prompt"]
            expected_policy = row["expected_policy"]
            
            start_time = time.time()
            
            # Pipeline
            language = detect_language(prompt)
            rule_time_start = time.time()
            rule_score = evaluate_rules(prompt)
            rule_latency_list.append(time.time() - rule_time_start)
            
            semantic_score = evaluate_semantic(prompt)
            pii_entities, safe_text, _ = analyze_and_anonymize(prompt, language)
            policy = evaluate_policy(rule_score, semantic_score, pii_entities)
            
            latency = time.time() - start_time
            latency_list.append(latency)
            
            decision = policy["decision"]
            
            # Record result
            results.append({
                "id": row["id"],
                "prompt": prompt,
                "language": row["language"],
                "expected_policy": expected_policy,
                "predicted_policy": decision,
                "rule_score": rule_score,
                "semantic_score": semantic_score,
                "latency_ms": int(latency * 1000)
            })
            
            # True label for blocking
            y_true_binary.append(1 if expected_policy == "BLOCK" else 0)
            y_pred_binary.append(1 if decision == "BLOCK" else 0)
            
            # Rule-only logic simulation for comparison
            # If rule > 0, BLOCK. Else, ALLOW.
            y_pred_rule_only.append(1 if rule_score > 0 else 0)

    # Save results CSV
    print("Saving evaluation_results.csv...")
    with open("results/evaluation_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Calculate metrics
    def get_metrics(y_true, y_pred):
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0)
        }

    hybrid_metrics = get_metrics(y_true_binary, y_pred_binary)
    rule_metrics = get_metrics(y_true_binary, y_pred_rule_only)
    
    metrics_summary = {
        "total_samples": len(results),
        "hybrid_approach": hybrid_metrics,
        "rule_only_approach": rule_metrics,
        "latency": {
            "hybrid_mean_ms": sum(latency_list) / len(latency_list) * 1000,
            "rule_only_mean_ms": sum(rule_latency_list) / len(rule_latency_list) * 1000
        }
    }

    print("Saving metrics_summary.json...")
    with open("results/metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=4)
        
    print("Evaluation Complete. Metrics:")
    print(json.dumps(metrics_summary, indent=2))

if __name__ == "__main__":
    run_evaluation()
