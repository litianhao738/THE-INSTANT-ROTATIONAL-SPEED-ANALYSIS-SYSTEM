import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from scipy.stats import zscore
from statsmodels.nonparametric.smoothers_lowess import lowess

data_folder = "RpmAna"
file_name = "run13.xlsx"
file_path = os.path.join(data_folder, file_name)

df = pd.read_excel(file_path)
df = df.iloc[1:]
df = df.apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

time = df.iloc[:, 0].values
voltage = df.iloc[:, 1].values

black_white_counts = []
current_count = 0
inside_positive = voltage[0] > 0

flag = 0
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

y_counts = np.array(black_white_counts)
x_points = np.arange(len(y_counts))

# Perform LOWESS fitting (Locally Weighted Regression)
smoothed = lowess(y_counts, x_points, frac=0.1, it=3)[:, 1]
#Compute residuals (actual value - fitted value)
residuals = y_counts - smoothed
#Compute Z-score and detect anomalies
z_scores = zscore(residuals)
threshold = 4
anomaly_indices = np.where(np.abs(z_scores) > threshold)[0]
anomaly_values = y_counts[anomaly_indices]

# Main plot (Full range)
fig, ax = plt.subplots(figsize=(10, 5))

ax.scatter(x_points, y_counts, color='black', s=3, label="Raw Data")

ax.plot(x_points, smoothed, color='green', linestyle='dashed', linewidth=1, label="LOWESS Fit")

scatter_anomalies = ax.scatter(anomaly_indices, anomaly_values, color='red', s=50, marker='x', label="Outliers")

ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("Data Points Count")
ax.legend()
ax.set_title("Outlier Detection for constant speed")
ax.grid(True)



fig_zoom, ax_zoom = plt.subplots(figsize=(10, 5))

ax_zoom.scatter(x_points, y_counts, color='black', s=3, label="Raw Data")

ax_zoom.plot(x_points, smoothed, color='green', linestyle='dashed', linewidth=1, label="LOWESS Fit")

scatter_zoom_anomalies = ax_zoom.scatter(anomaly_indices, anomaly_values, color='red', s=50, marker='x', label="Anomalies")

ax_zoom.set_xlim(100, 800)
ax_zoom.set_xlabel("Sequence number of zebra stripe pairs (Zoomed)")
ax_zoom.set_ylabel("Data Points Count")
ax_zoom.legend()
ax_zoom.set_title("Zoomed-In View (X: 100-800)")
ax_zoom.grid(True)

annotations = []

def setup_interactive_cursor(fig, scatter_anomalies):
    cursor = mplcursors.cursor(scatter_anomalies, multiple=True)

    @cursor.connect("add")
    def on_click(sel):
        x, y = sel.target
        annotation = sel.annotation
        annotation.set_text(f"x: {int(x)}\ny: {y:.2f}")
        annotation.set_fontsize(9)
        annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))
        annotations.append(annotation)

    def on_double_click(event):
        if event.dblclick and annotations:
            annotation = annotations.pop()
            annotation.set_visible(False)
            plt.gcf().canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_double_click)

setup_interactive_cursor(fig, scatter_anomalies)
setup_interactive_cursor(fig_zoom, scatter_zoom_anomalies)

plt.show()
