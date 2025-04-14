import pandas as pd
import os

data_folder = "RpmAna"

file_names = [
    "run56.xlsx"
]

for file in file_names:
    file_path = os.path.join(data_folder, file)

    df = pd.read_excel(file_path, usecols=[0, 1], skiprows=86)
    df.columns = ["S", "V"]

    df_cleaned = df.dropna()

    df_cleaned.to_excel(file_path, index=False)

    print(f"Data Cleaning finished: {file_path}")
