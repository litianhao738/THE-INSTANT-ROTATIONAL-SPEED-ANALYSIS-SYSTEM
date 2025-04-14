import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, probplot
from statsmodels.nonparametric.smoothers_lowess import lowess

data_folder = "RpmAna"
file_name = "run31.xlsx"
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

plt.figure(figsize=(6, 4))
plt.hist(residuals, bins=30, color='skyblue', edgecolor='black')
plt.title("Histogram of Residuals")
plt.xlabel("Residual Value")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig("Residual_Histogram.png", dpi=300)
plt.show()