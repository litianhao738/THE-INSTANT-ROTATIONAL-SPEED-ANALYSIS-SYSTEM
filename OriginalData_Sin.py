import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import random

# Define data file path
data_folder = "RpmAna"
file_name = "run55.xlsx"
file_path = os.path.join(data_folder, file_name)

# Load Excel file
df = pd.read_excel(file_path)

# Skip first row, convert to numeric, and remove NaNs
df = df.iloc[1:]
df = df.apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

# Extract time and voltage columns
time = df.iloc[:, 0].values
voltage = df.iloc[:, 1].values

# Count data points between black-white (positive-negative) transitions
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

# Prepare data for plotting
y_counts = np.array(black_white_counts)
x_points = np.arange(len(y_counts))

# =================== Main Plot ===================
plt.figure(figsize=(8, 2), dpi=400)
line, = plt.plot(x_points, y_counts, color='blue', linewidth=0.3, label="Data Points Count")

# Plot configuration
plt.xlabel("Black-White Stripe Pair Index", fontsize=3)
plt.ylabel("Data Points Count", fontsize=3)
plt.title("Data Points per Black-White Stripe", fontsize=5)
plt.legend(fontsize=3)
plt.grid(True, linestyle="--", linewidth=0.5)
plt.xticks(fontsize=5)
plt.yticks(fontsize=5)

# Enable interactive cursor annotations
annotations = []
cursor = mplcursors.cursor([line], hover=False, multiple=True)

@cursor.connect("add")
def on_click(sel):
    x, y = sel.target
    annotation = sel.annotation
    annotation.set_text(f"x: {x:.0f}\ny: {y:.0f}")
    annotation.set_fontsize(2)
    annotation.set_color("black")
    annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))
    annotations.append(annotation)

# Allow double-click to remove the latest annotation
def on_double_click(event):
    if event.dblclick:
        if annotations:
            annotation = annotations.pop()
            annotation.set_visible(False)
            plt.gcf().canvas.draw_idle()

plt.gcf().canvas.mpl_connect("button_press_event", on_double_click)
plt.tight_layout()
plt.savefig("Run53_Sinusoidal_Clickable_Annotations.png", dpi=400, bbox_inches='tight')
plt.show()

# =================== Zoomed-in Plot ===================

# Randomly select 1/4 of x range
total_points = len(x_points)
quarter_length = total_points // 4
start_idx = random.randint(0, total_points - quarter_length)
end_idx = start_idx + quarter_length

# Extract zoomed-in data
zoom_x = x_points[start_idx:end_idx]
zoom_y = y_counts[start_idx:end_idx]

# Create zoomed-in figure
plt.figure(figsize=(4, 1), dpi=300)
zoom_line, = plt.plot(zoom_x, zoom_y, color='red', linewidth=0.5, label="Zoomed Data Points Count")

# Zoomed plot configuration
plt.xlabel("Black-White Stripe Pair Index (Zoomed)", fontsize=5)
plt.ylabel("Data Points Count", fontsize=5)
plt.title("Zoomed Data Points per Black-White Stripe", fontsize=6)
plt.legend(fontsize=5)
plt.grid(True, linestyle="--", linewidth=0.5)
plt.xticks(fontsize=5)
plt.yticks(fontsize=5)

# Add interactive annotations to zoomed plot
zoom_annotations = []
zoom_cursor = mplcursors.cursor([zoom_line], hover=False, multiple=True)

@zoom_cursor.connect("add")
def on_zoom_click(sel):
    x, y = sel.target
    annotation = sel.annotation
    annotation.set_text(f"x: {x:.0f}\ny: {y:.0f}")
    annotation.set_fontsize(3)
    annotation.set_color("black")
    annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))
    zoom_annotations.append(annotation)

# Allow double-click to remove zoomed annotation
def on_zoom_double_click(event):
    if event.dblclick:
        if zoom_annotations:
            annotation = zoom_annotations.pop()
            annotation.set_visible(False)
            plt.gcf().canvas.draw_idle()

plt.gcf().canvas.mpl_connect("button_press_event", on_zoom_double_click)

plt.show()
