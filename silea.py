import sys
import os
import subprocess
import re

num_files = 10
sileapath = "./silea.jar"
wekapath = "./weka.jar"

# Assuming sys.argv[1] is the path to your CSV file
filename = sys.argv[1]
base_filename = os.path.splitext(filename)[0]
folder = os.path.dirname(filename)
print(folder)
# Step 7: Train with SILEA
percentages = []
for i in range(num_files):
    weka_command = ["java", "-jar", sileapath, "-i", f'{base_filename}_train_{i+1}.arff', f"-m {folder}/model -t -ga -g 10 -gp 0.5"]
    subprocess.run(' '.join(weka_command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    weka_command = ["java", "-jar", sileapath, "-i", f'{base_filename}_test_{i+1}.arff', f"-m {folder}/model -T -g 10"]
    result = subprocess.run(' '.join(weka_command), capture_output=True, text=True, shell=True)
    output = result.stdout
    for line in output.splitlines():
        if line.startswith("Correctly classified:"):
            match = re.search(r'\((\d+\.\d+)%\)', line)
            percentage = float(match.group(1))
            percentages.append(percentage)
            break
average = sum(percentages) / len(percentages)
print(average)
