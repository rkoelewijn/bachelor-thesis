import json
import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher

# Define paths exactly as requested
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent
GROUND_TRUTH_FILE = ROOT_DIR / "data" / "ground_truth_labels (1).json"
BASELINE_FILE = ROOT_DIR / "data" / "validation_results_baseline.json"
HYBRID_FILE = ROOT_DIR / "data" / "validation_results_hybrid.json"

def similar(a, b):
    """Calculates the similarity ratio between two strings."""
    if not a or not b: return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def load_data():
    """Loads the JSON files."""
    try:
        with open(GROUND_TRUTH_FILE, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
        with open(BASELINE_FILE, 'r', encoding='utf-8') as f:
            baseline_data = json.load(f)
        with open(HYBRID_FILE, 'r', encoding='utf-8') as f:
            hybrid_data = json.load(f)
        return gt_data, baseline_data, hybrid_data
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None

def map_nli_to_gt(nli_verdict):
    """Maps NLI verdicts to Ground Truth format for direct comparison."""
    mapping = {
        "ENTAILMENT": "TRUE",
        "CONTRADICTION": "FALSE",
        "UNSUPPORTED": "UNSUPPORTED"
    }
    return mapping.get(nli_verdict, "UNKNOWN")

def main():
    print("="*60)
    print("EVALUATING VALIDATION METHODS AGAINST GROUND TRUTH")
    print("="*60)

    gt_data, baseline_data, hybrid_data = load_data()
    if not gt_data: return

    # 1. Flatten Baseline Data
    baseline_records = []
    for item in baseline_data:
        artist = item.get("artist")
        for res in item.get("validation_results", []):
            baseline_records.append({
                "Artist": artist,
                "Claim": res.get("claim"),
                "Baseline_Verdict": res.get("nli_verdict")
            })
    df_baseline = pd.DataFrame(baseline_records)

    # 2. Flatten Hybrid Data
    hybrid_records = []
    for item in hybrid_data:
        artist = item.get("artist")
        for res in item.get("validation_results", []):
            hybrid_records.append({
                "Artist": artist,
                "Claim": res.get("claim"),
                "Hybrid_Verdict": res.get("nli_verdict"),
                "Hybrid_Status": res.get("hybrid_status"),
                "MB_Conflict_Flag": res.get("mb_conflict_flag")
            })
    df_hybrid = pd.DataFrame(hybrid_records)

    # 3. Process Ground Truth Data
    gt_records = []
    for item in gt_data:
        gt_records.append({
            "Artist": item.get("artist"),
            "Claim_GT": item.get("claim"),
            "Ground_Truth": item.get("ground_truth")
        })
    df_gt = pd.DataFrame(gt_records)

    # 4. Merge Baseline and Hybrid
    df_merged = pd.merge(df_baseline, df_hybrid, on=["Artist", "Claim"], how="outer")

    # 5. Fuzzy Match Ground Truth to Merged Claims
    # (Because the GT file claims sometimes have extra spaces or minor edits)
    mapped_gt = []
    for _, row in df_merged.iterrows():
        artist = row['Artist']
        claim = row['Claim']
        
        # Filter GT by artist to narrow the search space
        gt_subset = df_gt[df_gt['Artist'] == artist]
        
        best_match_score = 0
        best_gt = None
        
        for _, gt_row in gt_subset.iterrows():
            score = similar(claim, gt_row['Claim_GT'])
            if score > best_match_score:
                best_match_score = score
                best_gt = gt_row['Ground_Truth']
                
        # If the strings are at least 60% similar, we consider it a match
        if best_match_score > 0.6: 
            mapped_gt.append(best_gt)
        else:
            mapped_gt.append(None)

    df_merged['Ground_Truth'] = mapped_gt
    
    # 6. Apply mapping for baseline comparison
    df_merged['Baseline_Mapped'] = df_merged['Baseline_Verdict'].apply(map_nli_to_gt)

    # 7. Calculate Statistics
    df_valid_gt = df_merged.dropna(subset=['Ground_Truth'])
    total_matched = len(df_valid_gt)
    
    baseline_correct = (df_valid_gt['Baseline_Mapped'] == df_valid_gt['Ground_Truth']).sum()
    baseline_accuracy = (baseline_correct / total_matched) * 100

    # Cross-tabulate Hybrid Status vs Ground Truth
    hybrid_vs_gt = pd.crosstab(
        df_valid_gt['Hybrid_Status'], 
        df_valid_gt['Ground_Truth'], 
        margins=True, 
        margins_name="Total"
    )

    # 8. Output Results
    print(f"Matched {total_matched} generated claims with the Ground Truth dataset.\n")
    
    print(f"--- 1. BASELINE ACCURACY (Strict NLI) ---")
    print(f"Correct: {baseline_correct} / {total_matched}")
    print(f"Accuracy: {baseline_accuracy:.1f}%\n")
    
    print(f"--- 2. HYBRID METHOD BREAKDOWN ---")
    print("How the Hybrid categories align with human-labeled Ground Truth:")
    print("-" * 60)
    print(hybrid_vs_gt)
    print("-" * 60)
    
    # Optional: Save the aligned dataset to a CSV for manual review
    output_path = ROOT_DIR / "data" / "aligned_evaluation_results.csv"
    df_valid_gt.to_csv(output_path, index=False)
    print(f"\nSaved detailed claim-by-claim alignment to: {output_path}")

if __name__ == "__main__":
    main()