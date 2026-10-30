"""

This file is responsible for testing the lexical analyzer in isolation from the main code,
with the aim of verifying whether a specific new function is functional.

to execute: python -m unittest tests/test_lexer.py

"""

import unittest

from src.lexer.scanner import *
from src.lexer.token import *

class TestLexer(unittest.TestCase):
    
    def test_similarity(self):                                             
        similar_texts = ["opeini", "closa", "creati", "satrt"]
        for text in similar_texts:
            scanner = Scanner(text)
            scanner.scan()
            tokens = scanner.tokens[0]

            if tokens.type == TokenType.IDENTIFIER:
                print(f"Token is not an action:\n Type: {tokens.type} \n Lexeme: {tokens.lexeme}")
            else:
                print(f"token is a action:\n Type: {tokens.type} \n Lexeme: {tokens.lexeme}")
        

if __name__ == '__main__':
    unittest.main()
        