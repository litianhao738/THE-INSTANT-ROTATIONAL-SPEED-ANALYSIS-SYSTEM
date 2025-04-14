import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from scipy.ndimage import gaussian_filter1d

# Define the path to the Excel file
data_folder = "RpmAna"
file_name = "run55.xlsx"
file_path = os.path.join(data_folder, file_name)

# Read the Excel file using openpyxl engine
df = pd.read_excel(file_path, engine='openpyxl')

# Skip the first row, convert all data to numeric and drop rows with NaN
df = df.iloc[1:]
df = df.apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

# Extract time and voltage data
time = df.iloc[:, 0].values
voltage = df.iloc[:, 1].values

# Set the total number of expected zebra stripes
total_stripes = 221

# Count data points between two transitions (positive to negative or vice versa)
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

# Convert to numpy array for further processing
y_counts = np.array(black_white_counts)
x_points = np.arange(len(y_counts))

# Apply Gaussian filter to smooth the curve
y_filtered = gaussian_filter1d(y_counts, sigma=3)

# Calculate residuals between original and smoothed values
residuals = y_counts - y_filtered

# Use 4-sigma rule to define anomaly threshold
threshold = 4 * np.std(residuals) # it can be adjust
anomalies = np.abs(residuals) > threshold

# ========== Full plot ==========

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_points, y_counts, 'k.', markersize=3, label="Raw Data")
ax.plot(x_points, y_filtered, 'r-', linewidth=1, label="Gaussian Smoothed")

# Highlight detected anomalies
anomaly_points = ax.scatter(x_points[anomalies], y_counts[anomalies], color='red', s=50, marker='x', label="Anomalies")

# Set axis labels and title
ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("CutNumOfAcqDataPerTeeth")
ax.legend()
ax.set_title("Anomaly Detection using Gaussian Filter")
ax.grid(True)

annotations = []

# Enable interactive cursor annotation
cursor = mplcursors.cursor([ax], multiple=True)

@cursor.connect("add")
def on_click(sel):
    """ Display selected data point when clicked. """
    x, y = sel.target
    annotation = sel.annotation
    annotation.set_text(f"x: {int(x)}\ny: {y:.2f}")
    annotation.set_fontsize(9)
    annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))
    annotations.append(annotation)

def on_double_click(event):
    """ Double click to remove last annotation. """
    if event.dblclick:
        if annotations:
            annotation = annotations.pop()
            annotation.set_visible(False)
            plt.gcf().canvas.draw_idle()

plt.gcf().canvas.mpl_connect("button_press_event", on_double_click)

# ========== Zoomed-in plot ==========

fig_zoom, ax_zoom = plt.subplots(figsize=(10, 5))
ax_zoom.plot(x_points, y_counts, 'k.', markersize=3, label="Raw Data")
ax_zoom.plot(x_points, y_filtered, 'r-', linewidth=1, label="Gaussian Smoothed")

# Show anomalies in zoomed-in view
ax_zoom.scatter(x_points[anomalies], y_counts[anomalies], color='red', s=50, marker='x', label="Anomalies")

# Set x-axis zoom range
ax_zoom.set_xlim(300, 1500)
ax_zoom.set_xlabel("Sequence number of zebra stripe pairs (Zoomed)")
ax_zoom.set_ylabel("CutNumOfAcqDataPerTeeth")
ax_zoom.legend()
ax_zoom.set_title("Zoomed-In View (X: 100-800)")
ax_zoom.grid(True)

# Enable annotation in zoomed-in plot
cursor_zoom = mplcursors.cursor([ax_zoom], multiple=True)

@cursor_zoom.connect("add")
def on_click_zoom(sel):
    x, y = sel.target
    annotation = sel.annotation
    annotation.set_text(f"x: {int(x)}\ny: {y:.2f}")
    annotation.set_fontsize(9)
    annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))
    annotations.append(annotation)

# Bind double-click function to zoomed-in canvas as well
plt.gcf().canvas.mpl_connect("button_press_event", on_double_click)

# Show both plots
plt.show()
