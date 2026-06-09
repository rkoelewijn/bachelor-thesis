import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Data extracted from baseline_metrics.json
metrics_data = {
    "atomic_metrics": {
        "labels": ["SUPPORTED", "INTRINSIC", "EXTRINSIC"],
        "confusion_matrix": [
            [39, 12, 4],
            [1, 16, 3],
            [5, 5, 13]
        ],
        "precision_macro": 0.6672,
        "recall_macro": 0.6914,
        "f1_macro": 0.6628
    },
    "binary_metrics": {
        "accuracy": 0.7872,
        "error_detection_rate": 0.9643,
        "false_positive_rate": 0.4737,
        "f1_binary": 0.8437
    }
}

# ---------------------------------------------------------
# FIGURE 1: Confusion Matrix Heatmap
# ---------------------------------------------------------
def plot_confusion_matrix():
    cm = np.array(metrics_data["atomic_metrics"]["confusion_matrix"])
    labels = metrics_data["atomic_metrics"]["labels"]
    
    plt.figure(figsize=(8, 6))
    
    # Create a heatmap with a clean, academic color map (Blues)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels, 
                annot_kws={"size": 14}, cbar=True)
    
    plt.title('Baseline Confusion Matrix (Atomic Claims)', fontsize=15, pad=15)
    plt.ylabel('True Ground Truth Label', fontsize=12)
    plt.xlabel('Predicted NLI Label', fontsize=12)
    
    # Ensure layout fits well and save
    plt.tight_layout()
    plt.savefig('baseline_confusion_matrix.png', dpi=300)
    plt.show()

# ---------------------------------------------------------
# FIGURE 2: Performance Metrics Bar Charts
# ---------------------------------------------------------
def plot_performance_metrics():
    # Setup data for Atomic Metrics
    atomic_scores = [
        metrics_data["atomic_metrics"]["precision_macro"],
        metrics_data["atomic_metrics"]["recall_macro"],
        metrics_data["atomic_metrics"]["f1_macro"]
    ]
    atomic_labels = ['Precision (Macro)', 'Recall (Macro)', 'F1-Score (Macro)']
    
    # Setup data for Binary Metrics
    binary_scores = [
        metrics_data["binary_metrics"]["accuracy"],
        metrics_data["binary_metrics"]["f1_binary"],
        metrics_data["binary_metrics"]["error_detection_rate"],
        metrics_data["binary_metrics"]["false_positive_rate"]
    ]
    binary_labels = ['Accuracy', 'F1-Score (Binary)', 'Error Detection\nRate', 'False Positive\nRate']

    # Create subplots (1 row, 2 columns)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Color palettes
    color_atomic = '#2ca02c' # Greenish
    color_binary = '#1f77b4' # Blueish
    
    # Plot 1: Atomic Metrics
    sns.barplot(x=atomic_labels, y=atomic_scores, ax=axes[0], color=color_atomic)
    axes[0].set_title('Atomic Claim Level (Ternary)', fontsize=14, pad=10)
    axes[0].set_ylim(0, 1.0)
    axes[0].set_ylabel('Score', fontsize=12)
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add text labels on top of bars
    for i, v in enumerate(atomic_scores):
        axes[0].text(i, v + 0.02, f"{v:.3f}", ha='center', fontsize=11, fontweight='bold')

    # Plot 2: Binary Metrics
    sns.barplot(x=binary_labels, y=binary_scores, ax=axes[1], color=color_binary)
    axes[1].set_title('Sentence Level (Min-Pooling Aggregation)', fontsize=14, pad=10)
    axes[1].set_ylim(0, 1.0)
    axes[1].set_ylabel('Score', fontsize=12)
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add text labels on top of bars
    for i, v in enumerate(binary_scores):
        axes[1].text(i, v + 0.02, f"{v:.3f}", ha='center', fontsize=11, fontweight='bold')

    plt.suptitle('Baseline Evaluation Metrics Overview', fontsize=16, y=1.05)
    plt.tight_layout()
    plt.savefig('baseline_performance_metrics.png', dpi=300, bbox_inches='tight')
    plt.show()

# Run the visualization functions
plot_confusion_matrix()
plot_performance_metrics()