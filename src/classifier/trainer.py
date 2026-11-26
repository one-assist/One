
"""
Trains a classifier on the dataset and saves the model to a file.
"""

import json

from src.classifier.model import Classifier


# Loads the dataset from a JSON file and returns it as a list of texts and labels.
def load_dataset():
    with open('src/classifier/dataset/dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

        texts, labels = [], []
        for intent, examples in data.items():
            for example in examples:
                texts.append(example)
                labels.append(intent)

        return texts, labels

# Only executes this block of code if trainer.py is run.
if __name__ == '__main__':
    X, y = load_dataset()
    classifier = Classifier()
    model = classifier.train(X, y)
    classifier.save("src/classifier/model.joblib")
