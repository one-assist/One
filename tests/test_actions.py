
"""

This file is responsible for testing the actions commands in isolation from the main code,
with the aim of verifying whether a specific new function is functional.

to execute: python -m unittest tests/test_actions.py
"""
import unittest

from src.ast.checker import *
from src.classifier.model import *
from src.lexer.scanner import *


class TestActions(unittest.TestCase):

    def test_actions(self):
        command = "create task make a cake"

        print(f'command: {command}')
        classifier = Classifier()
        intent_object = classifier.get_intent(command)
        intent = intent_object.intent
        print(f'intent: {intent}')
        
        scanner = Scanner(command)
        scanner.scan()

        parser = Parser(scanner.tokens, intent)
        ast_root = parser.parse_command()

        if ast_root:
            ast_checker(ast_root)
if __name__ == '__main__':
    unittest.main()
        