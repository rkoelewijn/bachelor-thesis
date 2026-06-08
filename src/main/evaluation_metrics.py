import sys
import json
import pandas as pd
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# --- Path Alignment ---
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
# Assuming data is stored in a centralized data folder
PREDICTIONS_PATH = ROOT_DIR / "data" / "results" / "validation_results_hybrid.json"
GROUND_TRUTH_PATH = ROOT_DIR / "data" / "eval" / "hybrid_ground_truth_labels.json" # Change to hybrid_ground_truth_labels.json when testing the hybrid pipeline

def print_header():
    print("=" * 70)
    print("📊 CLOUDSPEAKERS PIPELINE EVALUATOR")
    print("=" * 70)

def load_json(filepath):
    if not filepath.exists():
        print(f"🚨 Error: Could not find file at {filepath}")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print_header()

    # 1. Load Data
    print(f"Loading predictions from: {PREDICTIONS_PATH.name}")
    predictions_raw = load_json(PREDICTIONS_PATH)
    
    print(f"Loading ground truth from: {GROUND_TRUTH_PATH.name}")
    ground_truth_raw = load_json(GROUND_TRUTH_PATH)

    if not predictions_raw or not ground_truth_raw:
        return

    # 2. Flatten the nested automated predictions into a tabular format
    pred_data = []
    for entry in predictions_raw:
        artist = entry.get("artist", "Unknown")
        # Support both 'validation_results' and 'claims' depending on your pipeline version
        validations = entry.get("validation_results", [])
        
        for idx, val in enumerate(validations):
            pred_data.append({
                "artist": artist,
                "claim": val.get("claim", ""),
                "nli_verdict": val.get("nli_verdict", "UNSUPPORTED") # Default to unsupported if missing
            })
            
    df_pred = pd.DataFrame(pred_data)

    # 3. Load the flat ground truth labels
    df_gt = pd.DataFrame(ground_truth_raw)

    # 4. Merge datasets on 'artist' and 'claim'
    df_merged = pd.merge(
        df_pred, 
        df_gt[['artist', 'claim', 'ground_truth']], 
        on=['artist', 'claim'], 
        how='inner'
    )

    # 5. Clean the data: Drop rows where the human label is null (invalid claims)
    initial_count = len(df_merged)
    df_merged = df_merged.dropna(subset=['ground_truth'])
    valid_count = len(df_merged)
    
    print(f"\nFiltered out {initial_count - valid_count} invalid/unlabeled claims.")
    print(f"Evaluating remaining {valid_count} valid claims...\n")

    # 6. Calculate Metrics
    y_true = df_merged['ground_truth']
    y_pred = df_merged['nli_verdict']
    
    # Calculate exact percentage match (Accuracy)
    accuracy = accuracy_score(y_true, y_pred)
    
    print("=" * 70)
    print(f"🎯 OVERALL PERCENTAGE MATCH (ACCURACY): {accuracy:.2%}")
    print("=" * 70 + "\n")

    # 7. Generate Table Overviews
    print("📋 DETAILED METRICS OVERVIEW:")
    print("-" * 70)
    # The classification report generates the Precision, Recall, and F1-Scores for each class
    report = classification_report(y_true, y_pred, labels=["SUPPORTED", "CONTRADICTION", "UNSUPPORTED"])
    print(report)
    
    print("🔀 CONFUSION MATRIX (True vs. Predicted):")
    print("-" * 70)
    # Create a nice cross-tabulation table to see exactly what the model confused
    conf_matrix = pd.crosstab(
        df_merged['ground_truth'], 
        df_merged['nli_verdict'], 
        rownames=['Actual (Human)'], 
        colnames=['Predicted (Model)'],
        margins=True
    )
    print(conf_matrix)
    print("\n" + "=" * 70)
    
    # 8. (Optional) Export Mismatches for qualitative analysis in your thesis
    mismatches = df_merged[df_merged['ground_truth'] != df_merged['nli_verdict']]
    mismatch_path = CURRENT_DIR / "error_analysis_mismatches.csv"
    mismatches.to_csv(mismatch_path, index=False)
    print(f"Exported {len(mismatches)} mismatched claims for error analysis to: {mismatch_path.name}")

if __name__ == "__main__":
    main()