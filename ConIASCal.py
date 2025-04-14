import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from scipy.stats import zscore
from statsmodels.nonparametric.smoothers_lowess import lowess

data_folder = "RpmAna"
file_name = "run36.xlsx"
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

smoothed = lowess(y_counts, x_points, frac=0.1, it=3)[:, 1]

residuals = y_counts - smoothed

z_scores = zscore(residuals)
threshold = 4 #Or 4.5
anomaly_indices = np.where(np.abs(z_scores) > threshold)[0]
anomaly_values = y_counts[anomaly_indices]

x_clean = np.delete(x_points, anomaly_indices)
y_clean = np.delete(y_counts, anomaly_indices)

linear_coeffs = np.polyfit(x_clean, y_clean, 1)
y_linear_fit = np.polyval(linear_coeffs, x_points)

#代入异常值，计算修正后的采样点数
y_fitted_full = np.copy(y_counts)
y_fitted_full[anomaly_indices] = y_linear_fit[anomaly_indices]

#  α
alpha_i = y_fitted_full / y_counts


start_index = 3
m = 221
#Calculate the number of complete 221 sets of black and white stripes in the data
num_laps = (len(alpha_i) - start_index)
theta_normals = []
# Iterate over all complete 221 sets of black and white stripes
for i in range(num_laps):
    start = start_index + i * m
    end = start + m
    if end <= len(alpha_i):
        sum_alpha = np.sum(alpha_i[start:end])
        theta_normals.append(360 / sum_alpha)
theta_normal = np.mean(theta_normals)

print(f"Corrected single stripe angular displacement: {theta_normal:.4f} degrees")


fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(x_points, y_counts, color='black', s=3, label="Raw Data")

# Green LOWESS fitted curve (Used for anomaly detection)
ax.plot(x_points, smoothed, color='green', linestyle='dashed', linewidth=1, label="LOWESS Fit")

scatter_anomalies = ax.scatter(anomaly_indices, anomaly_values, color='red', s=50, marker='x', label="Anomalies")
# Linear fit (solid blue line, using only data after removal of outliers)
ax.plot(x_points, y_linear_fit, color='blue', linestyle='-', linewidth=1, label="Linear Fit (No Outliers)")

ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("Data Points Count")
ax.legend()
ax.set_title("Anomaly Removal and Linear Fit")
ax.grid(True)

##IAS
f_c = 25600 #Change your frequency here!
time_intervals = y_fitted_full / f_c
IAS = theta_normal / time_intervals


fig, ax = plt.subplots(figsize=(10, 5))

# 绘制 IAS 主图
ax.plot(range(len(IAS)), IAS, 'm-', linewidth=1, label="Instantaneous Angular Speed (IAS)")
ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("Instantaneous Angular Speed (°/s)")
ax.legend()
ax.set_title("Calculated Instantaneous Angular Speed (IAS)")
ax.grid(True)

# 创建局部放大图
fig_zoom, ax_zoom = plt.subplots(figsize=(10, 5))

# 放大 X 轴范围（如 100-1000 之间）
ax_zoom.plot(range(len(IAS)), IAS, 'm-', linewidth=1, label="Instantaneous Angular Speed (IAS)")
ax_zoom.set_xlim(100, 1000)
ax_zoom.set_xlabel("Sequence number of zebra stripe pairs (Zoomed)")
ax_zoom.set_ylabel("Instantaneous Angular Speed (°/s)")
ax_zoom.legend()
ax_zoom.set_title("Zoomed-In View (X: 100-800)")
ax_zoom.grid(True)

# 交互功能
annotations = []

def setup_interactive_cursor(fig, ax):
    cursor = mplcursors.cursor(ax, hover=True)

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

# 绑定交互功能到两张图
setup_interactive_cursor(fig, ax)
setup_interactive_cursor(fig_zoom, ax_zoom)

plt.show()


print(f"IAS Mean: {np.mean(IAS):.4f} °/s")
print(f"IAS Std Dev: {np.std(IAS):.4f} °/s")
'--------------------------------------------------------'
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 5))

#Plot raw data (including outliers)
ax.scatter(x_points, y_counts, color='black', s=3, label="Original Data (Including Outliers)")

#Plot detected anomalies
ax.scatter(anomaly_indices, y_counts[anomaly_indices], color='red', s=50, marker='x', label="Detected outliers")

#  Plot linear fit curve
ax.plot(x_points, y_linear_fit, color='blue', linestyle='-', linewidth=1, label="Linear Fit (No Outliers)")

# Plot only corrected data (Replaced outliers, marked in green)
ax.scatter(anomaly_indices, y_fitted_full[anomaly_indices], color='green', s=50, marker='o', label="Replaced Outliers")


ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("Data Points Count (Correctedz)")
ax.legend()
ax.set_title("Comparison")
ax.grid(True)

plt.show()
### ==== Original IAS Analysis (Based on raw y_counts without removing outliers) ====
# Set the ADC sampling frequency (same as in the main code)
f_c = 25600#Change your frequency here!

# Assume all original alpha_i are 1, i.e., no correction applied
alpha_raw = np.ones_like(y_counts)

# Parameters consistent with main code
start_index = 3
m = 221
num_laps_raw = (len(alpha_raw) - start_index)

# Calculate theta_raw: estimated angular displacement from raw data (in degrees)
theta_normals_raw = []
for i in range(num_laps_raw):
    start = start_index + i * m
    end = start + m
    if end <= len(alpha_raw):
        sum_alpha = np.sum(alpha_raw[start:end])  # Should be 221 in most cases
        theta_normals_raw.append(360 / sum_alpha)

theta_raw = np.mean(theta_normals_raw)

# Compute raw IAS (without outlier removal)
time_intervals_raw = y_counts / f_c
IAS_raw = theta_raw / time_intervals_raw

print(f"Raw IAS Std Dev: {np.std(IAS_raw):.4f} °/s")
