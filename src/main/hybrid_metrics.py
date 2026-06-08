import json
from pathlib import Path
from sklearn.metrics import f1_score, accuracy_score, recall_score, confusion_matrix, precision_score
from collections import Counter

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
RAW_HYBRID_DATA_PATH = ROOT_DIR / "data" / "results" / "validation_results_hybrid.json"

def calculate_metrics(y_true_binary, y_pred_binary, y_true_ternary, y_pred_ternary):
    """Helper function to calculate all metrics for a given set of predictions."""
    # Binary (Sentence/Atomic Error)
    acc_bin = accuracy_score(y_true_binary, y_pred_binary)
    f1_bin = f1_score(y_true_binary, y_pred_binary, zero_division=0)
    recall_bin = recall_score(y_true_binary, y_pred_binary, zero_division=0)
    
    tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # Ternary (Atomic Macro)
    labels = ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]
    macro_prec = precision_score(y_true_ternary, y_pred_ternary, labels=labels, average='macro', zero_division=0)
    macro_rec = recall_score(y_true_ternary, y_pred_ternary, labels=labels, average='macro', zero_division=0)
    macro_f1 = f1_score(y_true_ternary, y_pred_ternary, labels=labels, average='macro', zero_division=0)
    
    counts = Counter(y_pred_ternary)
    
    return {
        "acc": acc_bin, "f1_bin": f1_bin, "error_det": recall_bin, "fpr": fpr,
        "mac_prec": macro_prec, "mac_rec": macro_rec, "mac_f1": macro_f1,
        "counts": counts
    }

def main():
    print("="*80)
    print("BASELINE VS. HYBRID METRICS COMPARISON (LOCKED T=70.0)")
    print("="*80)

    if not RAW_HYBRID_DATA_PATH.exists():
        print(f"Error: Could not find data at {RAW_HYBRID_DATA_PATH}")
        return

    with open(RAW_HYBRID_DATA_PATH, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    # Tracking lists
    y_true_sent, y_base_sent, y_hybrid_sent = [], [], []
    y_true_claims, y_base_claims, y_hybrid_claims = [], [], []

    locked_t = 70.0

    for entry in corpus:
        base_sentence_supported = True
        hybrid_sentence_supported = True
        has_valid_gt = False
        true_sentence_supported = True

        for eval_data in entry.get("validation_results", []):
            gt_label = eval_data.get('ground_truth', 'UNKNOWN')
            
            if gt_label not in ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]:
                continue
                
            has_valid_gt = True

            # 1. RECONSTRUCT THE BASELINE PREDICTION
            ent = eval_data.get('best_ent_score', 0)
            con = eval_data.get('best_con_score', 0)
            
            if ent >= locked_t and ent > con:
                base_verdict = "SUPPORTED"
            elif con >= locked_t and con > ent:
                base_verdict = "INTRINSIC"
            else:
                base_verdict = "EXTRINSIC"

            # 2. GET THE HYBRID PREDICTION (Saved in file)
            hybrid_verdict = eval_data.get('nli_verdict')

            y_true_claims.append(gt_label)
            y_base_claims.append(base_verdict)
            y_hybrid_claims.append(hybrid_verdict)

            # Min-Pooling tracking
            if gt_label != "SUPPORTED":
                true_sentence_supported = False
            if base_verdict != "SUPPORTED":
                base_sentence_supported = False
            if hybrid_verdict != "SUPPORTED":
                hybrid_sentence_supported = False

        if has_valid_gt:
            y_true_sent.append(0 if true_sentence_supported else 1)
            y_base_sent.append(0 if base_sentence_supported else 1)
            y_hybrid_sent.append(0 if hybrid_sentence_supported else 1)

    # Prepare Binary Atomic arrays (0=SUPPORTED, 1=ERROR)
    y_true_claims_bin = [0 if l == "SUPPORTED" else 1 for l in y_true_claims]
    y_base_claims_bin = [0 if l == "SUPPORTED" else 1 for l in y_base_claims]
    y_hybrid_claims_bin = [0 if l == "SUPPORTED" else 1 for l in y_hybrid_claims]

    # Calculate Everything
    base_sent = calculate_metrics(y_true_sent, y_base_sent, y_true_claims, y_base_claims)
    hybrid_sent = calculate_metrics(y_true_sent, y_hybrid_sent, y_true_claims, y_hybrid_claims)
    
    base_atom = calculate_metrics(y_true_claims_bin, y_base_claims_bin, y_true_claims, y_base_claims)
    hybrid_atom = calculate_metrics(y_true_claims_bin, y_hybrid_claims_bin, y_true_claims, y_hybrid_claims)

    gt_counts = Counter(y_true_claims)

    # --- PRINT THE THESIS TABLES ---
    print(f"\n{'METRIC':<35} | {'BASELINE PIPELINE':<20} | {'HYBRID PIPELINE':<20}")
    print("-" * 80)
    
    print("\n[SENTENCE LEVEL]")
    print(f"{'Sentence F1-Score':<35} | {base_sent['f1_bin']:<20.4f} | {hybrid_sent['f1_bin']:<20.4f}")
    print(f"{'Sentence Accuracy':<35} | {base_sent['acc']:<20.4f} | {hybrid_sent['acc']:<20.4f}")
    print(f"{'Error Detection Rate (Recall)':<35} | {base_sent['error_det']:<20.4f} | {hybrid_sent['error_det']:<20.4f}")
    print(f"{'False Positive Rate':<35} | {base_sent['fpr']:<20.4f} | {hybrid_sent['fpr']:<20.4f}")

    print("\n[ATOMIC LEVEL]")
    print(f"{'Atomic F1-Score (Macro)':<35} | {base_atom['mac_f1']:<20.4f} | {hybrid_atom['mac_f1']:<20.4f}")
    print(f"{'Atomic Precision (Macro)':<35} | {base_atom['mac_prec']:<20.4f} | {hybrid_atom['mac_prec']:<20.4f}")
    print(f"{'Atomic Recall (Macro)':<35} | {base_atom['mac_rec']:<20.4f} | {hybrid_atom['mac_rec']:<20.4f}")
    print(f"{'Atomic Accuracy (Binary)':<35} | {base_atom['acc']:<20.4f} | {hybrid_atom['acc']:<20.4f}")
    print(f"{'Atomic Error Detection':<35} | {base_atom['error_det']:<20.4f} | {hybrid_atom['error_det']:<20.4f}")
    print(f"{'Atomic False Positive Rate':<35} | {base_atom['fpr']:<20.4f} | {hybrid_atom['fpr']:<20.4f}")

    print("\n[PREDICTION DISTRIBUTIONS]")
    print(f"{'Predicted SUPPORTED':<35} | {base_atom['counts'].get('SUPPORTED', 0):<20} | {hybrid_atom['counts'].get('SUPPORTED', 0):<20}")
    print(f"{'Predicted EXTRINSIC':<35} | {base_atom['counts'].get('EXTRINSIC', 0):<20} | {hybrid_atom['counts'].get('EXTRINSIC', 0):<20}")
    print(f"{'Predicted INTRINSIC':<35} | {base_atom['counts'].get('INTRINSIC', 0):<20} | {hybrid_atom['counts'].get('INTRINSIC', 0):<20}")
    
    print(f"\nGround Truth SUPPORTED: {gt_counts.get('SUPPORTED', 0)}")
    print(f"Ground Truth EXTRINSIC: {gt_counts.get('EXTRINSIC', 0)}")
    print(f"Ground Truth INTRINSIC: {gt_counts.get('INTRINSIC', 0)}")
    print("=" * 80)

if __name__ == "__main__":
    main()