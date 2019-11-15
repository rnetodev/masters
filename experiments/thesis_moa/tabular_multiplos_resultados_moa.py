# tabular_multiplos_resultados_moa.py
import os
import os.path
import re
import sys

import pandas as pd

# Mappings
map_filename_algorithm = {
    "rbfchain": "RBFChain",
    "adwin": "ADWIN",
    "cusum": "CUSUM",
    "ddm": "DDM",
    "eddm": "EDDM",
    "ewma": "EWMA",
    "hddma": "HDDMA",
    "ph": "PageHinkley",
    "seqdrift1": "SeqDrift1",
}

map_path_dataset = {
    "nochange": "Sem Mudança",
    "abrupt": "Mudança Abrupta",
    "gradual": "Mudança Gradual",
    "incremental": "Mudança Incremental",
}

output_row_template = {
    "Algoritmo": None,
    "TP": 0.0,
    "MR": 0.0,
    "VP": 0,
    "FP": 0,
    "ATR": 0.0,
}

table = {
    filename: output_row_template.copy() for filename in map_filename_algorithm.keys()
}

# Params
path = sys.argv[1]
files = os.listdir(path)

# Dataset used
dataset = None
dataset_key = None

for key in map_path_dataset:
    if key in path:
        dataset_key = key
        dataset = map_path_dataset[dataset_key]
        break

# Processing
for file in files:
    file_absolute_path = os.path.abspath(os.path.join(path, file))
    filename = file.replace(".csv", "")

    algorithm = map_filename_algorithm[filename]

    df = pd.read_csv(file_absolute_path)

    table_row = table[filename]

    table_row["Algoritmo"] = algorithm
    table_row["TP"] = float(
        df.iloc[-1]["evaluation time (cpu seconds)"]
        / df["evaluation time (cpu seconds)"].size
    )
    table_row["MR"] = int(df.iloc[-1]["true changes"])
    try:
        table_row["ATR"] = float(df.iloc[-1]["delay detection (average)"])
    except ValueError:
        table_row["ATR"] = 0

    # Counting VP and FP
    true_changes = 0
    detected_changes = 0
    pending_drift = False

    for index, row in df.iterrows():
        if row["true changes"] > true_changes:
            true_changes += 1
            pending_drift = True

        if row["detected changes"] > detected_changes:
            detected_changes += 1

            if pending_drift:
                table_row["VP"] += 1
                pending_drift = False
            else:
                table_row["FP"] += 1

# Printing
print("*" * 80)
print(f"*** {dataset_key:^72} ***")
print("*" * 80)
print()
print()

print("\\toprule")

headers = []
for header in output_row_template.keys():
    headers.append(f"{header:<22}")

print(" & ".join(headers), end=" \\\\ ")
print()

print("\\midrule")
for filename in table:
    row = table[filename]
    print(f"{row['Algoritmo']:<22}", end=" & ")
    print(f"{row['TP']:<22.3f}", end=" & ")
    print(f"{row['MR']:<22}", end=" & ")
    print(f"{row['VP']:<22}", end=" & ")
    print(f"{row['FP']:<22}", end=" & ")
    print(f"{row['ATR']:<22.2f}", end=" \\\\ ")
    print()
print("\\bottomrule")
