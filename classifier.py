import sys
import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC

# Function to choose a classifier
def choose_classifier(choice):
    if choice == '1':
        return DecisionTreeClassifier()
    elif choice == '2':
        return SVC()
    else:
        print("Invalid choice. Defaulting to Decision Tree Classifier.")
        return DecisionTreeClassifier()

# Assuming sys.argv[1] is the path to your CSV file
filename = sys.argv[1]
base_filename = os.path.splitext(filename)[0]

percentages = []
num_files = 10  # or however many you want

for i in range(num_files):
    train_file_path = f'{base_filename}_train_{i+1}.csv'
    test_file_path = f'{base_filename}_test_{i+1}.csv'

    # Load the training and test data
    train_data = pd.read_csv(train_file_path)
    test_data = pd.read_csv(test_file_path)

    X_train = train_data.iloc[:, :-1].values
    y_train = train_data.iloc[:, -1].values
    X_test = test_data.iloc[:, :-1].values
    y_test = test_data.iloc[:, -1].values

    # Let the user choose the classifier only once before the loop
    if i == 0:
        classifier = choose_classifier(sys.argv[2])

    # Train the chosen classifier
    classifier.fit(X_train, y_train)

    # Make predictions on the test data
    predictions = classifier.predict(X_test)

    # Calculate the accuracy
    accuracy = accuracy_score(y_test, predictions)
    percentages.append(accuracy)

# Calculate and print the average accuracy
average = sum(percentages) / len(percentages)
print(average * 100)
