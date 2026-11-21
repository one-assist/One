"""This file provides an intent classification model using a Naive Bayes classifier."""

from dataclasses import dataclass

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


@dataclass
class IntentResult:
    intent: str
    confidence: float

class Classifier:
    def __init__(self, path: str | None = "src/classifier/model.joblib", threshold: float = 0.11):
        self.pipeline = None
        if path:
            self.model = self.load(path)
        self.threshold = threshold

    # Train the classifier on the given text and labels.
    # Vectorizes the text and fits a Naive Bayes classifier.
    def train(self, text: list[str], labels: list[str]):
        self.pipeline = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2)), 
            LogisticRegression(max_iter=1000)
        )
        # Fit the pipeline on the text and labels.
        self.pipeline = self.pipeline.fit(text, labels)

    # Get the intent of the given text.
    def get_intent(self, text: str | None):
        if not self.model:
            raise ValueError("Model not loaded")

        if text is None:
            return IntentResult(intent="UNKNOWN", confidence=0.0)

        probabilities = self.model.predict_proba([text])[0]
        max_idx = probabilities.argmax()
        confidence = float(probabilities[max_idx])
        intent = self.model.classes_[max_idx]

        if confidence < self.threshold:
            
            return IntentResult(intent="UNKNOWN", confidence=confidence)
        return IntentResult(intent=intent, confidence=confidence)
    
    # Save the model to a file using joblib.
    def save(self, path: str):
        joblib.dump(self.pipeline, path)

    def load(self, path: str):
        return joblib.load(path)