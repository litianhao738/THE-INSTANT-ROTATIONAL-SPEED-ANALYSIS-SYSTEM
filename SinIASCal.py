import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from scipy.ndimage import gaussian_filter1d

data_folder = "RpmAna"
file_name = "run53.xlsx"
file_path = os.path.join(data_folder, file_name)

df = pd.read_excel(file_path, engine='openpyxl')

df = df.iloc[1:]
df = df.apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

time = df.iloc[:, 0].values
voltage = df.iloc[:, 1].values

total_stripes = 221

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

# Convert lists to NumPy arrays
y_counts = np.array(black_white_counts)
x_points = np.arange(len(y_counts))

# Apply Gaussian filter to smooth the data
y_filtered = gaussian_filter1d(y_counts, sigma=3)

# Calculate residuals (errors)
residuals = y_counts - y_filtered

# Use 3σ rule to identify anomalies
threshold = 4 * np.std(residuals)
anomalies = np.abs(residuals) > threshold

# Fourier fitting after removal of anomalies
x_clean = x_points[~anomalies]
y_clean = y_counts[~anomalies]
# Normalise x data to improve stability of fit
x_scaled = x_clean / np.max(x_clean)
# Fourier series fitting
def fourier_fit(x, y, n_harmonics=250):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    T = x[-1] - x[0]
    w = 2 * np.pi / T

    A = np.zeros((len(x), 2 * n_harmonics + 1))
    A[:, 0] = 1

    for i in range(n_harmonics):
        A[:, 2 * i + 1] = np.cos((i + 1) * w * x)
        A[:, 2 * i + 2] = np.sin((i + 1) * w * x)

    coeffs = np.linalg.lstsq(A, y, rcond=None)[0]

    y_fit = A.dot(coeffs)

    return y_fit, coeffs

y_fit, coeffs = fourier_fit(x_clean, y_clean, n_harmonics=250)

# Calculate the Y-value for all data points (including outliers)
def fourier_eval(x, coeffs, x_ref, n_harmonics=250):
    x = np.array(x, dtype=float)
    T = x_ref[-1] - x_ref[0]
    w = 2 * np.pi / T

    A = np.zeros((len(x), 2 * n_harmonics + 1))
    A[:, 0] = 1

    for i in range(n_harmonics):
        A[:, 2 * i + 1] = np.cos((i + 1) * w * x)
        A[:, 2 * i + 2] = np.sin((i + 1) * w * x)

    y_fit_all = A.dot(coeffs)

    return y_fit_all



y_fitted_full = fourier_eval(x_points, coeffs, x_clean, n_harmonics=250)
#print("Original Anomalous Y values:", y_counts[anomalies])
#print("Corrected Y values:", y_fitted_full[anomalies])

# α
alpha_i = y_fitted_full / y_counts
"""
start_index = 3  
m = 221 
theta_normal = 360 / np.sum(alpha_i[start_index:start_index + m])
theta_buttjoint = alpha_i * theta_normal 
"""

start_index = 3
m = 221
num_laps = (len(alpha_i) - start_index)
theta_normals = []

for i in range(num_laps):
    start = start_index + i * m
    end = start + m
    if end <= len(alpha_i):
        sum_alpha = np.sum(alpha_i[start:end])
        theta_normals.append(360 / sum_alpha)

theta_normal = np.mean(theta_normals)

theta_buttjoint = alpha_i * theta_normal
print(f"Corrected single stripe angular displacement: {theta_normal:.4f} degrees")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_points, y_counts, 'k.', markersize=3, label="Raw Data")
ax.plot(x_clean, y_fit, 'b-', linewidth=1, label="Fourier Fit (No Outliers)")
ax.plot(x_points, y_fitted_full, 'g--', linewidth=1, label="Full Fourier Fit")

# Highlight anomalies
ax.scatter(x_points[anomalies], y_counts[anomalies], color='red', s=50, marker='x', label="Anomalies")

ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("CutNumOfAcqDataPerTeeth")
ax.legend()
ax.set_title("Anomaly Removal and Fourier Fit with Correction")
ax.grid(True)

mplcursors.cursor(hover=True)

plt.show()

f_c = 100000#Change your frequency here!

# Δt
time_intervals = y_fitted_full / f_c

# IAS
IAS = theta_normal / time_intervals


fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(range(len(IAS)), IAS, 'm-', linewidth=1, label="Instantaneous Angular Speed (IAS)")
ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("Instantaneous Angular Speed (°/s)")
ax.legend()
ax.set_title("Calculated Instantaneous Angular Speed (IAS)")
ax.grid(True)


fig_zoom, ax_zoom = plt.subplots(figsize=(10, 5))
ax_zoom.plot(range(len(IAS)), IAS, 'm-', linewidth=1, label="IAS (Zoomed)")
ax_zoom.set_xlim(100, 1000)
ax_zoom.set_xlabel("Sequence number of zebra stripe pairs (Zoomed)")
ax_zoom.set_ylabel("Instantaneous Angular Speed (°/s)")
ax_zoom.legend()
ax_zoom.set_title("Zoomed-In View (X: 100-1000)")
ax_zoom.grid(True)

def setup_interactive_cursor(fig, ax):
    cursor = mplcursors.cursor(ax, hover=True)

    @cursor.connect("add")
    def on_hover(sel):
        x, y = sel.target
        sel.annotation.set_text(f"x: {int(x)}\ny: {y:.2f}")
        sel.annotation.set_fontsize(9)
        sel.annotation.set_bbox(dict(facecolor="white", edgecolor="black", boxstyle="round"))

setup_interactive_cursor(fig, ax)
setup_interactive_cursor(fig_zoom, ax_zoom)

plt.show()

print(f"IAS Mean: {np.mean(IAS):.4f} °/s")
print(f"IAS Std Dev: {np.std(IAS):.4f} °/s")


import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(x_points, y_counts, color='black', s=3, label="Original Data (Including Outliers)")
ax.scatter(x_points[anomalies], y_counts[anomalies], color='red', s=50, marker='x', label="Detected Outliers")
ax.plot(x_clean, y_fit, color='blue', linestyle='-', linewidth=1, label="Fourier Fit (No Outliers)")
ax.scatter(x_points[anomalies], y_fitted_full[anomalies], color='green', s=50, marker='o', label="Replaced Outliers")
ax.set_xlabel("Sequence number of zebra stripe pairs")
ax.set_ylabel("CutNumOfAcqDataPerTeeth")
ax.legend()
ax.set_title("Comparison")
ax.grid(True)

plt.show()
### ==== Original IAS Analysis (Based on raw y_counts without removing outliers) ====
# Set the ADC sampling frequency (same as in the main code)
f_c = 100000#Change your frequency here!

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