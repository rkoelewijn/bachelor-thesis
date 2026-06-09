import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent 
RESULTS_FILE = ROOT_DIR / "data" / "results" / "validation__treshold_results_baseline.json"
def plot_score_histogram():
    if not RESULTS_FILE.exists():
        print(f"Error: Could not find the file at {RESULTS_FILE}")
        return

    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ent_scores = []

    # Extract only entailment scores for simplicity (since Contradiction is just the inverse)
    for entry in data:
        for val in entry.get('raw_validations', []):
            ent_scores.append(val.get('best_ent_score', 0))

    plt.figure(figsize=(9, 6))
    
    # Standard histogram with 10 bins (0-10%, 10-20%, etc.)
    sns.histplot(ent_scores, bins=10, color='#1f77b4', edgecolor='black', alpha=0.7)

    plt.title('Frequency of XLM-ROBERTa Entailment Scores', fontsize=14, pad=15)
    plt.xlabel('Predicted Entailment Confidence (%)', fontsize=12)
    plt.ylabel('Number of Atomic Claims', fontsize=12)
    
    plt.xlim(0, 100)
    plt.xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(CURRENT_DIR / 'score_histogram_plot.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    plot_score_histogram()