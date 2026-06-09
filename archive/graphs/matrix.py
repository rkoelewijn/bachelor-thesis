import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Setup robust paths
CURRENT_DIR = Path(__file__).resolve().parent

def plot_correctness_matrix():
    # Axes:
    # Rows: Actual INCORRECT (Positive), Actual CORRECT (Negative)
    # Cols: Correctly Predicted (Match), Incorrectly Predicted (Mismatch)
# Matrix Layout:
# [[TP, FN],
#  [FP, TN]]
    cm = np.array([
        [28, 0],
        [9, 10]
    ])
    
    # Calculate row percentages (based on Actual Ground Truth)
    row_sums = cm.sum(axis=1, keepdims=True)
    cm_percentages = cm / row_sums
    
    # Define the explicit terms for each quadrant
    terms = [
        ["TP", "FN"],
        ["FP", "TN"]
    ]
    
    # Create custom annotations combining terms, counts, and percentages
    annot_data = np.empty_like(cm).astype(str)
    for i in range(2):
        for j in range(2):
            annot_data[i, j] = f"{terms[i][j]}\n{cm[i, j]}" # ({cm_percentages[i, j]*100:.1f}%)

    # Labels for the axes
    x_labels = ["Negative", "Positive"]
    y_labels = ["False", "True"]
    
    # Setup plot
    plt.figure(figsize=(9, 6))
    
    # Use a clean blue color map to indicate this is a custom correctness grid
    sns.heatmap(cm, annot=annot_data, fmt='', cmap='Blues', 
                xticklabels=x_labels, yticklabels=y_labels, 
                annot_kws={"size": 13, "weight": "bold"}, cbar=False)
    
    plt.title('Sentence Level Prediction Match Grid', fontsize=15, pad=15)
    # plt.ylabel('Ground Truth Class', fontsize=12, fontweight='bold')
    # plt.xlabel('Pipeline Outcome', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    # Save the figure to your current directory
    plt.savefig(CURRENT_DIR / 'baseline_prediction_match_grid.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    plot_correctness_matrix()