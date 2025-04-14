import os
import numpy as np
import pandas as pd

# Define the folder and file to be read
data_folder = "RpmAna"
file_name = "run13.xlsx"
file_path = os.path.join(data_folder, file_name)

# Load the Excel file into a DataFrame
df = pd.read_excel(file_path)

# Skip the first row (often headers or metadata)
df = df.iloc[1:]

# Convert all values to numeric, setting errors to NaN
df = df.apply(pd.to_numeric, errors='coerce')

# Drop rows with any NaN values
df.dropna(inplace=True)

# Extract time and voltage values from the first and second columns
time = df.iloc[:, 0].values
voltage = df.iloc[:, 1].astype(float).values

# Count black-white transitions (positive to negative voltage and vice versa)
black_white_counts = []
current_count = 0
inside_positive = voltage[0] > 0
flag = 0

for i in range(1, len(voltage)):
    current_count += 1
    # Detect positive to negative transition
    if inside_positive and voltage[i] < 0:
        flag += 1
        inside_positive = False
    # Detect negative to positive transition
    elif not inside_positive and voltage[i] > 0:
        flag += 1
        inside_positive = True

    # One full cycle (positive -> negative -> positive or vice versa) detected
    if flag == 2:
        black_white_counts.append(current_count)
        flag = 0
        current_count = 0

# Convert list to numpy array for further processing
y_counts = np.array(black_white_counts)
x_points = np.arange(len(y_counts))

# Function to compute autocorrelation at a given lag
def autocorrelation(x, lag):
    return np.corrcoef(x[:-lag], x[lag:])[0, 1]

# Compute autocorrelation values for lags from 1 up to 100 or half the length of y_counts
lags = np.arange(1, min(100, len(y_counts) // 2))
autocorr_values = [autocorrelation(y_counts, lag) for lag in lags]

# Define a linear function (for potential future fitting, unused here)
def linear_func(x, a, b):
    return a * x + b

# Determine the type of motion based on autocorrelation characteristics
if max(autocorr_values) < 0.4:
    result = "Constant Speed Motion"
elif max(autocorr_values) > 0.6:
    result = "Sinusoidal Motion"
else:
    result = "Uncertain (Possibly Slightly Fluctuating Constant Speed)"

# Output the final classification result and the maximum autocorrelation value
print(f"Detection Result: {result}")
print(f"Maximum Autocorrelation Value: {max(autocorr_values):.4f}")
