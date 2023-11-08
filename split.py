import subprocess
import csv
import random
from collections import defaultdict
import sys
import os
import pandas as pd
import shutil
import glob
import re
import sys
import os
import csv
from collections import defaultdict
import random

sileapath = "./silea.jar"
wekapath = "./weka.jar"
num_files = 10

# Helper function to check if a string can be converted to float
def is_convertible(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# New Step 0: Create a function to encode categorical columns
def encode_categorical_columns(dataset, categorical_indices):
    # For each categorical column, create a dictionary to map text to numbers
    encodings = {index: {text: i for i, text in enumerate(set(column))} for index, column in categorical_indices.items()}
    # Now encode the dataset
    encoded_dataset = []
    for row in dataset:
        new_row = list(row)  # Copy the row
        for index, text in enumerate(row):
            if index in categorical_indices:
                new_row[index] = encodings[index][text]
        encoded_dataset.append(new_row)
    return encoded_dataset, encodings

# Assuming sys.argv[1] is the path to your CSV file
filename = sys.argv[1]
base_filename = os.path.splitext(filename)[0]

# Read the CSV file and store data
with open(filename, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader)
    data = [[-1 if cell == '' else cell for cell in row] for row in reader]

# Identify the indices of the categorical columns
# This is a simple heuristic that checks if the value can be converted to a float
categorical_indices = {index: [row[index] for row in data] for index, value in enumerate(header) if not all(is_convertible(row[index]) for row in data)}

# Step 1: Encode the categorical columns
encoded_data, encodings = encode_categorical_columns(data, categorical_indices)

# Group by labels (assuming the label is the last column)
label_groups = defaultdict(list)
for row in encoded_data:
    label = row[-1]  # Assuming the label is the last column
    label_groups[label].append(row)

# Step 2: Split into 10 parts
split_label_groups = {label: [] for label in label_groups}
for label, rows in label_groups.items():
    # random.shuffle(rows)
    # Split into 10 parts as evenly as possible
    split_label_groups[label] = [rows[i::num_files] for i in range(num_files)]

# Step 3: Create balanced datasets
datasets = []
for i in range(num_files):
    dataset = []
    for label, splits in split_label_groups.items():
        dataset.extend(splits[i])
    # random.shuffle(dataset)  # Shuffle the dataset to mix the labels
    datasets.append(dataset)

# Step 4: Write the datasets to separate files
for i, dataset in enumerate(datasets):
    with open(f'{base_filename}_{i+1}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header
        writer.writerows(dataset)

# Step 5: Create CSV and ARFF files
for i in range(num_files):
    shutil.copyfile(f'{base_filename}_{i+1}.csv', f'{base_filename}_test_{i+1}.csv')

    weka_command = ["java", "-cp", wekapath, "weka.core.converters.CSVLoader", f'{base_filename}_test_{i+1}.csv', ">", f'{base_filename}_test_{i+1}.arff']
    subprocess.run(' '.join(weka_command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    filenames_train = []

    for j in range(num_files):
        if i != j:
            filenames_train.append(f'{base_filename}_{j+1}.csv')
    
    # Initialize an empty list to store the dataframes
    dataframes = []

    # Loop through the list of filenames and read each one into a DataFrame
    for file in filenames_train:
        df = pd.read_csv(file)
        dataframes.append(df)

    # Concatenate all the dataframes into one, ignoring the index
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Write the merged DataFrame to a new CSV file, without the index
    merged_df.to_csv(f'{base_filename}_train_{i+1}.csv', index=False)

    weka_command = ["java", "-cp", wekapath, "weka.core.converters.CSVLoader", f'{base_filename}_train_{i+1}.csv', ">", f'{base_filename}_train_{i+1}.arff']
    subprocess.run(' '.join(weka_command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

# Step 6: Remove leftover files
# Use glob to find all files matching the pattern 'abc_*.csv'
file_pattern = f'{base_filename}_*.csv'
files = glob.glob(file_pattern)

# Compile a regular expression to match only files where * is a number
numbered_files = re.compile(rf'{base_filename}_\d+\.csv$')

# Loop through the files and delete each one
for file in files:
    if numbered_files.match(file):
        os.remove(file)
