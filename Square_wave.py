import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Read Excel data
data_folder = "RpmAna"
file_name = "run13.xlsx"
file_path = f"{data_folder}/{file_name}"

df = pd.read_excel(file_path)

# 2. Preprocess data
df = df.iloc[1:]  # Remove non-numeric rows
df = df.apply(pd.to_numeric, errors='coerce')  # Convert to numeric data
df.dropna(inplace=True)  # Remove invalid data

# Extract sampling point indices (X-axis) and raw voltage signal (Y-axis)
voltage = df.iloc[:, 1].values  # Raw voltage signal
sampling_index = np.arange(len(voltage))  # X-axis: Sampling point indices

# 3. Detect transition points in the raw voltage signal (only keep negative-to-positive transitions)
diff_voltage = np.diff(voltage)
threshold_change = 0.5  # Change threshold
transitions = np.where((diff_voltage > threshold_change))[0] + 1  # Only keep negative-to-positive transitions

# 4. Compute the number of sampling points per black-and-white stripe
stripe_counts = []
for i in range(len(transitions) - 1):
    start = transitions[i]
    end = transitions[i + 1]
    count = end - start  # Number of sampling points per stripe pair
    stripe_counts.append(count)

if len(stripe_counts) > 0:
    stripe_counts = np.array(stripe_counts)
else:
    print("No complete stripe pairs detected.")
    exit()

# 5. Generate X-axis and Y-axis dynamically based on sampling indices and stripe widths
x_points = []  # Store dynamic X-axis points (sampling indices)
y_points = []  # Store dynamic Y-axis points (raw voltage values)

current_idx = 0
for count in stripe_counts:
    cycle_x = sampling_index[current_idx:current_idx + count]
    cycle_y = voltage[current_idx:current_idx + count]
    x_points.extend(cycle_x)
    y_points.extend(cycle_y)
    current_idx += count

x_points = np.array(x_points)
y_points = np.array(y_points)

# 6. Plot the overall raw voltage signal
plt.figure(figsize=(10, 4))
plt.step(x_points, y_points, where='post', label="Raw Voltage Signal (Dynamic Width)", color='blue', linewidth=1)
plt.xlabel("Sampling Point Index")
plt.ylabel("Voltage (V)")
plt.title("Raw Voltage Signal with Dynamic Stripe Widths (Full View)")
plt.grid(True, linestyle="--", linewidth=0.5)
plt.legend()
plt.show()

# 7. Plot a zoomed-in view of the raw voltage signal
start_idx = 0
end_idx = 3000

mask = (x_points >= start_idx) & (x_points <= end_idx)
x_zoom = x_points[mask]
y_zoom = y_points[mask]

if len(x_zoom) != len(y_zoom):
    print(f"Warning: x_zoom and y_zoom lengths do not match - x: {len(x_zoom)}, y: {len(y_zoom)}")
    if len(y_zoom) > len(x_zoom):
        y_zoom = y_zoom[:len(x_zoom)]
    elif len(x_zoom) > len(y_zoom):
        x_zoom = x_zoom[:len(y_zoom)]

plt.figure(figsize=(10, 4))
plt.step(x_zoom, y_zoom, where='post', label="Raw Voltage Signal (Zoomed-In, Dynamic Width)", color='blue', linewidth=1)
plt.xlabel("Sampling Point Index")
plt.ylabel("Voltage (V)")
plt.title("Raw Voltage Signal with Dynamic Stripe Widths (Zoomed-In View)")
plt.grid(True, linestyle="--", linewidth=0.5)
plt.legend()
plt.show()

# 8. Compute the binarization threshold based on the example paper (Figure 12)
v_max = np.max(voltage)
v_min = np.min(voltage)
threshold_binary = (v_max + v_min) / 2  # Mean of maximum and minimum values

# 9. Perform binarization
binary_voltage = np.where(voltage >= threshold_binary, 10, 0)  # Below threshold: 0V, above threshold: 10V

# 10. Regenerate X-axis and Y-axis for the binary signal based on dynamic stripe widths
binary_x_points = []
binary_y_points = []

current_idx = 0
for count in stripe_counts:
    cycle_x = sampling_index[current_idx:current_idx + count]
    cycle_y = binary_voltage[current_idx:current_idx + count]
    binary_x_points.extend(cycle_x)
    binary_y_points.extend(cycle_y)
    current_idx += count

binary_x_points = np.array(binary_x_points)
binary_y_points = np.array(binary_y_points)

# 11. Plot the overall binary square wave signal
plt.figure(figsize=(10, 4))
plt.step(binary_x_points, binary_y_points, where='post', label="Binary Square Wave (Dynamic Width)", color='red', linewidth=1)
plt.xlabel("Sampling Point Index")
plt.ylabel("Voltage (V)")
plt.title("Binary Square Wave Signal (Full View, Dynamic Width)")
plt.grid(True, linestyle="--", linewidth=0.5)
plt.legend()
plt.show()

# 12. Plot a zoomed-in view of the binary square wave signal
binary_mask = (binary_x_points >= start_idx) & (binary_x_points <= end_idx)
binary_x_zoom = binary_x_points[binary_mask]
binary_y_zoom = binary_y_points[binary_mask]

if len(binary_x_zoom) != len(binary_y_zoom):
    print(f"Warning: binary_x_zoom and binary_y_zoom lengths do not match - x: {len(binary_x_zoom)}, y: {len(binary_y_zoom)}")
    if len(binary_y_zoom) > len(binary_x_zoom):
        binary_y_zoom = binary_y_zoom[:len(binary_x_zoom)]
    elif len(binary_x_zoom) > len(binary_y_zoom):
        binary_x_zoom = binary_x_zoom[:len(binary_y_zoom)]

plt.figure(figsize=(10, 4))
plt.step(binary_x_zoom, binary_y_zoom, where='post', label="Binary Square Wave (Zoomed-In, Dynamic Width)", color='red', linewidth=1)
plt.xlabel("Sampling Point Index")
plt.ylabel("Voltage (V)")
plt.title("Binary Square Wave Signal (Zoomed-In View, Dynamic Width)")
plt.grid(True, linestyle="--", linewidth=0.5)
plt.legend()
plt.show()
