import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

# Define the path to the Excel file
data_folder = "RpmAna"
file_name = "run13.xlsx"
file_path = os.path.join(data_folder, file_name)

# Read the Excel file
df = pd.read_excel(file_path)

# Skip the first row, convert to numeric values, drop missing data
df = df.iloc[1:]
df = df.apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

# Extract time and voltage columns
time = df.iloc[:, 0].values
voltage = df.iloc[:, 1].values

# Initialize variables for counting black-white transitions
black_white_counts = []
current_count = 0
inside_positive = voltage[0] > 0
flag = 0

# Count the number of data points between two polarity reversals
for i in range(1, len(voltage)):
    current_count += 1
    if inside_positive and voltage[i] < 0:
        flag += 1
        inside_positive = False
    elif not inside_positive and voltage[i] > 0:
        flag += 1
        inside_positive = True

    if flag == 2:
        black_white_counts.append(current_count)
        flag = 0
        current_count = 0

# Prepare data for plotting and anomaly detection
y_counts = np.array(black_white_counts)
x_points = np.arange(len(y_counts))

# Calculate a threshold based on the top 1% longest intervals
y_counts_sorted = np.sort(y_counts)
q99_index = int(len(y_counts) * 0.99)
threshold = np.mean(y_counts_sorted[q99_index:])

print(f"Selected threshold (99% last 2 values): {threshold:.2f}")

# Identify anomalies exceeding the threshold
anomaly_indices = np.where(y_counts > threshold)[0]
anomaly_values = y_counts[anomaly_indices]

# Calculate intervals between anomalies
anomaly_diffs = np.diff(anomaly_indices)

# --- First full plot with all data ---

plt.figure(figsize=(12, 3), dpi=400)
line, = plt.plot(x_points, y_counts, color='blue', linewidth=0.3, label="Data Points Count")
scatter = plt.scatter(anomaly_indices, anomaly_values, color='red', s=3, label="Anomalies", zorder=6)

plt.xlabel("Black-White Stripe Pair Index", fontsize=5)
plt.ylabel("Data Points Count", fontsize=5)
plt.title("Data Points per Black-White Stripe ", fontsize=5)
plt.legend(fontsize=5)
plt.grid(True, linestyle="--", linewidth=0.5)
plt.xticks(fontsize=5)
plt.yticks(fontsize=5)

# Enable interactive annotations using mouse click
annotations = []
cursor = mplcursors.cursor([line, scatter], hover=False, multiple=True)

@cursor.connect("add")
def on_click(sel):
    x, y = sel.target
    annotation = sel.annotation
    annotation.set_text(f"x: {x:.0f}\ny: {y:.0f}")
    annotation.set_fontsize(3)
    annotation.set_color("black")
    annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))
    annotations.append(annotation)

# Double-click to remove the most recent annotation
def on_double_click(event):
    if event.dblclick:
        if annotations:
            annotation = annotations.pop()
            annotation.set_visible(False)
            plt.gcf().canvas.draw_idle()

plt.gcf().canvas.mpl_connect("button_press_event", on_double_click)

# Label interval values between anomalies on the plot
for i in range(len(anomaly_diffs)):
    plt.annotate(f"{anomaly_diffs[i]}",
                 (anomaly_indices[i], anomaly_values[i]),
                 textcoords="offset points", xytext=(0, 10), ha='center', fontsize=2, color='red')

# Save and show the full plot
plt.savefig("Run13_Clickable_Annotations.png", dpi=400, bbox_inches='tight')
plt.show()

# --- Second zoomed-in plot (x-axis 0 to 2000) ---

plt.figure(figsize=(12, 3), dpi=400)
plt.plot(x_points[:2000], y_counts[:2000], color='blue', linewidth=0.3, label="Data Points Count")
plt.scatter(anomaly_indices[anomaly_indices < 2000], anomaly_values[anomaly_indices < 2000],
            color='red', s=3, label="Anomalies", zorder=6)

plt.xlabel("Black-White Stripe Pair Index", fontsize=5)
plt.ylabel("Data Points Count", fontsize=5)
plt.title("Zoomed Data Points per Black-White Stripe", fontsize=5)
plt.legend(fontsize=5)
plt.grid(True, linestyle="--", linewidth=0.5)
plt.xticks(fontsize=5)
plt.yticks(fontsize=5)

# Label interval values between anomalies on the zoomed-in plot
zoomed_anomalies = anomaly_indices[anomaly_indices < 2000]
zoomed_diffs = np.diff(zoomed_anomalies)

for i in range(len(zoomed_diffs)):
    plt.annotate(f"{zoomed_diffs[i]}",
                 (zoomed_anomalies[i], anomaly_values[anomaly_indices < 2000][i]),
                 textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color='red')

# Save and show the zoomed-in plot
plt.savefig("Run13_Zoomed_0-2000.png", dpi=400, bbox_inches='tight')
plt.show()
