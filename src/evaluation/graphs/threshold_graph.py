import matplotlib.pyplot as plt

# The exact data extracted from your pipeline
threshold_data =[ [
                0.0,
                0.45180664535503245
            ],
            [
                5.0,
                0.6012142283328724
            ],
            [
                10.0,
                0.6383651436283015
            ],
            [
                15.0,
                0.6456084567539676
            ],
            [
                20.0,
                0.660934514504082
            ],
            [
                25.0,
                0.660934514504082
            ],
            [
                30.0,
                0.6585605038236618
            ],
            [
                35.0,
                0.6480070546737214
            ],
            [
                40.0,
                0.6628082492321195
            ],
            [
                45.0,
                0.6628082492321195
            ],
            [
                50.0,
                0.6628082492321195
            ],
            [
                55.0,
                0.654119814497173
            ],
            [
                60.0,
                0.654119814497173
            ],
            [
                65.0,
                0.6321762747652252
            ],
            [
                70.0,
                0.6448184084630416
            ],
            [
                75.0,
                0.6218663797859428
            ],
            [
                80.0,
                0.6349767699882116
            ],
            [
                85.0,
                0.6279540458711791
            ],
            [
                90.0,
                0.6369425689755773
            ],
            [
                95.0,
                0.6103567451882058
            ],
            [
                100.0,
                0.12672176308539948
            ]
] 
# Unpack the data into X and Y lists
thresholds = [item[0] for item in threshold_data]
f1_scores = [item[1] for item in threshold_data]

# Define the optimal point to highlight
optimal_t = 40
optimal_f1 = 0.6628082492321195

# Set up the academic plot style
plt.figure(figsize=(10, 6))
plt.plot(thresholds, f1_scores, marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=6)

# Highlight the start of the optimal threshold plateau
plt.axvline(x=optimal_t, color='red', linestyle='--', alpha=0.8, 
            label=rf'Optimal Threshold Plateau ($\mathcal{{T}} \geq {optimal_t}$)')
plt.scatter([optimal_t], [optimal_f1], color='red', zorder=5, s=80)

# Formatting for thesis readability
plt.title('Baseline Macro F1-Score vs. Confidence Threshold ($\mathcal{T}$)', fontsize=14, pad=15)
plt.xlabel('Confidence Threshold ($\mathcal{T}$)', fontsize=12)
plt.ylabel('Macro F1-Score', fontsize=12)

# --- NEW: Set Axis Limits and Ticks ---
plt.ylim(0.0, 1.0)
plt.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
plt.xticks([0, 10 , 20, 30, 40, 50, 60, 70, 80, 90, 100])

plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right', fontsize=11)

# Save the figure as a high-resolution PNG
plt.tight_layout()
plt.savefig('threshold_optimization_plot.png', dpi=300)

# Display the plot
plt.show()