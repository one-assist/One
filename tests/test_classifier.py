
"""
Test cases for the Classifier model.
"""
import unittest
from src.classifier.model import * 


class TestClassifier(unittest.TestCase):
    def test_get_intent(self):
        classifier = Classifier()
        intent_object = classifier.get_intent("open the firefox")

        confidence = intent_object.confidence
        intent = intent_object.intent

        print(f"Intent: {intent}, Confidence: {confidence}")

if __name__ == '__main__':
    unittest.main()