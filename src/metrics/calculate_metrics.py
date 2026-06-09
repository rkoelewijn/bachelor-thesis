import json
from pathlib import Path
from sklearn.metrics import f1_score, accuracy_score, recall_score, confusion_matrix, precision_score
from collections import Counter

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
RAW_HYBRID_DATA_PATH = ROOT_DIR / "data" / "results" / "validation_results_hybrid.json"

def main():
    print("="*60)
    print("HYBRID METRICS CALCULATOR (FROM CHECKPOINT)")
    print("="*60)

    if not RAW_HYBRID_DATA_PATH.exists():
        print(f"Error: Could not find raw hybrid data at {RAW_HYBRID_DATA_PATH}")
        return

    with open(RAW_HYBRID_DATA_PATH, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    # 1. Initialize tracking lists
    y_true_sentences = []
    y_pred_sentences = []
    
    y_true_claims = []
    y_pred_claims = []

    # 2. Extract the saved data
    for entry in corpus:
        # Sentence level (Only include if it has a valid ground truth)
        if 'sentence_ground_truth' in entry:
            # Map INCORRECT (hallucinated) to 1, CORRECT to 0
            y_true_sentences.append(1 if entry['sentence_ground_truth'] == "INCORRECT" else 0)
            y_pred_sentences.append(1 if entry['sentence_verdict_pred'] == "INCORRECT" else 0)

        # Atomic level
        for eval_data in entry.get("validation_results", []):
            gt_label = eval_data.get('ground_truth', 'UNKNOWN')
            pred_label = eval_data.get('nli_verdict')

            if gt_label in ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]:
                y_true_claims.append(gt_label)
                y_pred_claims.append(pred_label)

    # 3. Calculate Sentence Metrics (Binary)
    sent_f1 = f1_score(y_true_sentences, y_pred_sentences, zero_division=0)
    sent_acc = accuracy_score(y_true_sentences, y_pred_sentences)
    sent_error_detection = recall_score(y_true_sentences, y_pred_sentences, zero_division=0)
    
    s_tn, s_fp, s_fn, s_tp = confusion_matrix(y_true_sentences, y_pred_sentences, labels=[0, 1]).ravel()
    sent_fpr = s_fp / (s_fp + s_tn) if (s_fp + s_tn) > 0 else 0.0

    # 4. Calculate Atomic Metrics (Ternary & Binary)
    labels = ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]
    
    # Ternary (Macro)
    atomic_macro_prec = precision_score(y_true_claims, y_pred_claims, labels=labels, average='macro', zero_division=0)
    atomic_macro_rec = recall_score(y_true_claims, y_pred_claims, labels=labels, average='macro', zero_division=0)
    atomic_macro_f1 = f1_score(y_true_claims, y_pred_claims, labels=labels, average='macro', zero_division=0)
    
    # Counts
    gt_counts = Counter(y_true_claims)
    pred_counts = Counter(y_pred_claims)

    # Convert Atomic to Binary for Accuracy, Error Detection and FPR (SUPPORTED = 0, Errors = 1)
    y_true_claims_binary = [0 if label == "SUPPORTED" else 1 for label in y_true_claims]
    y_pred_claims_binary = [0 if label == "SUPPORTED" else 1 for label in y_pred_claims]

    atomic_acc_binary = accuracy_score(y_true_claims_binary, y_pred_claims_binary)
    atomic_error_detection = recall_score(y_true_claims_binary, y_pred_claims_binary, zero_division=0)
    
    a_tn, a_fp, a_fn, a_tp = confusion_matrix(y_true_claims_binary, y_pred_claims_binary, labels=[0, 1]).ravel()
    atomic_fpr = a_fp / (a_fp + a_tn) if (a_fp + a_tn) > 0 else 0.0

    # 5. Print out the exact requested metrics list
    print("\n[SENTENCE LEVEL METRICS (BINARY)]")
    print(f"Sentence F1 score:                {sent_f1:.4f}")
    print(f"Sentence Accuracy:                {sent_acc:.4f}")
    print(f"Sentence Error Detection Rate:    {sent_error_detection:.4f}")
    print(f"Sentence False Positive Rate:     {sent_fpr:.4f}")

    print("\n[ATOMIC LEVEL METRICS]")
    print(f"Atomic Precision (Macro):         {atomic_macro_prec:.4f}")
    print(f"Atomic Recall (Macro):            {atomic_macro_rec:.4f}")
    print(f"Atomic F1 score (Macro):          {atomic_macro_f1:.4f}")
    print("-" * 40)
    print(f"Atomic Accuracy (Binary):         {atomic_acc_binary:.4f}")
    print(f"Atomic Error Detection Rate:      {atomic_error_detection:.4f}")
    print(f"Atomic False Positive Rate:       {atomic_fpr:.4f}")

    print("\n[LABEL COUNTS]")
    print(f"Predicted Supported Labels:       {pred_counts.get('SUPPORTED', 0)}")
    print(f"Predicted Extrinsic Labels:       {pred_counts.get('EXTRINSIC', 0)}")
    print(f"Predicted Intrinsic Labels:       {pred_counts.get('INTRINSIC', 0)}")
    print("-" * 40)
    print(f"Ground Truth Supported Labels:    {gt_counts.get('SUPPORTED', 0)}")
    print(f"Ground Truth Extrinsic Labels:    {gt_counts.get('EXTRINSIC', 0)}")
    print(f"Ground Truth Intrinsic Labels:    {gt_counts.get('INTRINSIC', 0)}")

if __name__ == "__main__":
    main()