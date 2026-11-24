import unittest

from src.audio.speech import *

class TestSpeech(unittest.TestCase):
    def test_speech_piper(self):
        text = "Hello, Good morning"
        speech1(text)


if __name__ == '__main__':
    unittest.main()