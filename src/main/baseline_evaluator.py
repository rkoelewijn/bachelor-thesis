import time
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import f1_score, confusion_matrix, precision_score, recall_score, accuracy_score

# Setup paths relative to the script location
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
EXPORT_PATH = ROOT_DIR / "data" / "results" / "validation__treshold_results_baseline.json"
GROUND_TRUTH_PATH = ROOT_DIR / "data" / "eval" / "ternary_ground_truth_labels.json"
METRICS_EXPORT_PATH = ROOT_DIR / "data" / "results" / "baseline_metrics.json" 
RAW_EXPORT_PATH = ROOT_DIR / "data" / "results" / "raw_validation_results.json"
CONFIDENCE_THRESHOLD = 70.0 
# Internal modules
import data_loader
import dutch_parser
import decomposer
import validator 

# --- NUMPY TO JSON ENCODER ---
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def print_header():
    print("="*60)
    print("CLOUDSPEAKERS BASELINE EVALUATOR")
    print("="*60)

def load_ground_truths(filepath):
    """Loads and flattens the ground truth JSON into a claim -> label dictionary."""
    if not filepath.exists():
        print(f"WARNING: Ground truth file missing at {filepath}")
        return {}
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    flat_gt = {}
    
    if isinstance(data, list):
         for item in data:
             claim = item.get('claim')
             ground_truth = item.get('ground_truth')
             
             # Only add to map if both exist and ground_truth is not null
             if claim and ground_truth:
                 flat_gt[claim] = ground_truth
                 
    return flat_gt

def main():
    """ 
    The evaluator loads the manually compiled corpus, extracts atomic claims, 
    generates raw NLI scores, calculates the optimal confidence threshold, 
    and applies min-pooling aggregation to evaluate sentence factuality.
    """
    start_time = time.time()
    print_header()
    
    # Load evaluation dataset 
    corpus = data_loader.get_evaluation_corpus()
    if not corpus:
        print("Data loading error.")
        return
        
    # Load and map external ground truth labels
    gt_map = load_ground_truths(GROUND_TRUTH_PATH)
    print(f"Loaded {len(gt_map)} ground truth labels.")
    print(f"Loaded {len(corpus)} valid artist entries for evaluation.\n")
    
    final_output_data = [] 
    all_evaluations = [] 

    print("STAGE 1: GENERATING RAW NLI SCORES")
    print("-" * 60)
    
    for entry in corpus:
        artist = entry.get("artist", "Unknown")
        summary = entry.get("summary", "")
        dutch_text = entry.get("dutch_text", "")

        print(artist)

        context_sentences = dutch_parser.prepare_dutch_sentences(dutch_text, artist)
        claims = decomposer.extract_claims(summary, artist)
        evaluations = validator.validate_claims(claims, context_sentences)

        for eval_data in evaluations:
            claim_text = eval_data.get('claim', '')
            # Fetch from the loaded JSON map rather than the entry object
            eval_data['ground_truth'] = gt_map.get(claim_text, "UNKNOWN") 
            all_evaluations.append(eval_data)

        entry["raw_validations"] = evaluations
        final_output_data.append(entry)

    # --- NEW STAGE 1.5: DECOUPLE INFERENCE FROM EVALUATION ---
    print("\nSTAGE 1.5: EXPORTING RAW PREDICTIONS")
    print("-" * 60)
    RAW_EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, cls=NpEncoder, ensure_ascii=False)
    print(f"Saved {len(all_evaluations)} raw claim evaluations to: {RAW_EXPORT_PATH}")
    print("You can now build secondary scripts to analyze this file without re-running the model!")


    # print("\nSTAGE 2: THRESHOLD OPTIMIZATION (F1 Maximization)")
    # print("-" * 60)
    # best_t = 0.0
    # best_f1 = 0.0
    
    valid_evals = [e for e in all_evaluations if e.get('ground_truth') in ['SUPPORTED', 'INTRINSIC', 'EXTRINSIC']]
    y_true_claims = [e['ground_truth'] for e in valid_evals]
    
    # if not y_true_claims:
    #      print("WARNING: No valid ground truth labels matched the extracted claims. Optimization will fail.")
    # else:
    #     thresholds = np.arange(0.0, 105.0, 5.0) 
    #     f1_scores_threshold = [] 

    #     for t in thresholds:
    #         y_pred_claims = []
    #         for eval_data in valid_evals:
    #             ent = eval_data.get('best_ent_score', 0)
    #             con = eval_data.get('best_con_score', 0)
                
    #             if ent >= t and ent > con:
    #                 y_pred_claims.append("SUPPORTED")
    #             elif con >= t and con > ent:
    #                 y_pred_claims.append("INTRINSIC")
    #             else:
    #                 y_pred_claims.append("EXTRINSIC")
                    
    #         current_f1 = f1_score(y_true_claims, y_pred_claims, average='macro', zero_division=0)

    #         f1_scores_threshold.append((t, current_f1))
            
    #         if current_f1 > best_f1:
    #             best_f1 = current_f1
    #             best_t = t
    best_t = CONFIDENCE_THRESHOLD   
    print(f"Optimal Confidence Threshold (T): {best_t:.2f})")


    print("\nSTAGE 3: LABEL ASSIGNMENT & MIN-POOLING AGGREGATION")
    print("-" * 60)
    
    y_true_sentences = []
    y_pred_sentences = []

    for entry in final_output_data:
        sentence_claims_supported = True
        true_sentence_claims_supported = True
        has_valid_ground_truth = False
        
        for eval_data in entry["raw_validations"]:
            ent = eval_data.get('best_ent_score', 0)
            con = eval_data.get('best_con_score', 0)
            gt_label = eval_data.get('ground_truth')
            
            # --- 1. Predictions ---
            if ent >= best_t and ent > con:
                verdict = "SUPPORTED"
            elif con >= best_t and con > ent:
                verdict = "INTRINSIC"
                sentence_claims_supported = False
            else:
                verdict = "EXTRINSIC"
                sentence_claims_supported = False
                
            eval_data['nli_verdict'] = verdict
            
            # --- 2. Ground Truth Derivation ---
            if gt_label in ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]:
                has_valid_ground_truth = True
                if gt_label != "SUPPORTED":
                    true_sentence_claims_supported = False
        
        # Binary Sentence Evaluation (SAFE Min-Pooling logic)
        pred_sentence_verdict = "CORRECT" if sentence_claims_supported else "INCORRECT"
        entry['sentence_verdict_pred'] = pred_sentence_verdict
        
        # Derive sentence ground truth using min-pooling
        if has_valid_ground_truth:
            true_sentence_verdict = "CORRECT" if true_sentence_claims_supported else "INCORRECT"
            entry['sentence_ground_truth'] = true_sentence_verdict
            
            y_true_sentences.append(true_sentence_verdict)
            y_pred_sentences.append(pred_sentence_verdict)


    print("\nSTAGE 4: BASELINE EVALUATION METRICS & EXPORT")
    print("-" * 60)
    
    if y_true_claims:
        final_y_pred_claims = [e['nli_verdict'] for e in valid_evals]
            
        labels = ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]
        conf_matrix_atomic = confusion_matrix(y_true_claims, final_y_pred_claims, labels=labels)
        macro_prec = precision_score(y_true_claims, final_y_pred_claims, average='macro', zero_division=0)
        macro_rec = recall_score(y_true_claims, final_y_pred_claims, average='macro', zero_division=0)
        macro_f1 = f1_score(y_true_claims, final_y_pred_claims, average='macro', zero_division=0)

        print("--- Atomic Claim Level (Ternary) ---")
        print("Confusion Matrix:")
        print(conf_matrix_atomic)
        print(f"Precision (Macro): {macro_prec:.4f}")
        print(f"Recall (Macro):    {macro_rec:.4f}")
        print(f"F1-Score (Macro):  {macro_f1:.4f}")
    
    if y_true_sentences:
        accuracy = accuracy_score(y_true_sentences, y_pred_sentences)

        y_true_binary = [1 if v == "INCORRECT" else 0 for v in y_true_sentences]
        y_pred_binary = [1 if v == "INCORRECT" else 0 for v in y_pred_sentences]
        
        error_detection_rate = recall_score(y_true_binary, y_pred_binary, zero_division=0)
        binary_f1 = f1_score(y_true_binary, y_pred_binary, zero_division=0)

        tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        print("\n--- Binary Sentence Level (Min-Pooling) ---")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Error Detection Rate (Recall on INCORRECT): {error_detection_rate:.4f}")
        print(f"False Positive Rate: {false_positive_rate:.4f}")
        print(f"F1-Score (Binary): {binary_f1:.4f}")

        # --- JSON METRICS EXPORT ---
        metrics_export = {
            # "threshold_data": {
            #     "optimal_threshold": float(best_t), 
            #     "threshold values": f1_scores_threshold,
            # },
            "atomic_metrics": {
                "labels": labels,
                "confusion_matrix": conf_matrix_atomic.tolist(),
                "precision_macro": float(macro_prec),
                "recall_macro": float(macro_rec),
                "f1_macro": float(macro_f1)
            },
            "binary_metrics": {
                "accuracy": float(accuracy),
                "error_detection_rate": float(error_detection_rate),
                "false_positive_rate": float(false_positive_rate),
                "f1_binary": float(binary_f1)
            }
        }
        
        METRICS_EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(METRICS_EXPORT_PATH, 'w', encoding='utf-8') as f:
            # Using NpEncoder here to prevent the int64 crash
            json.dump(metrics_export, f, indent=4, cls=NpEncoder)
        print(f"\nSaved metrics summary to: {METRICS_EXPORT_PATH}")
    else:
        print("\nSentence ground truth labels missing or derivable. Skipping binary metrics and export.")

    # Export pipeline dataset
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving complete baseline evaluation dataset to: {EXPORT_PATH}")
    
    with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, indent=4, cls=NpEncoder, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"Baseline Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()