"""

This file is responsible for testing the parser in isolation from the main code,
with the aim of verifying whether a specific new function is functional.

to execute: python -m unittest tests/test_parser.py

"""

import unittest

from src.parser.parser import *
from src.lexer.scanner import *
from src.classifier.model import *

class TestParser(unittest.TestCase):
    
    def parser_result(self, text: str):
        classifier = Classifier()
        intent_object = classifier.get_intent(text)
        intent = intent_object.intent
        
        scanner = Scanner(text)
        scanner.scan()
        
        parser = Parser(scanner.tokens, intent)
        return parser.parse_command()

    def ast_example(self, node: CommandExpr):
        
        if isinstance(node, SequenceAction):
            self.ast_example(node.left)
            self.ast_example(node.right)

        if isinstance(node, SingleAction):
            print(f"intent: {node.intent}, target: {node.target}")
         
    # Tests the AND connector, which executes two or more separate commands.
    def test_and(self):
        #There are three separate commands that will be executed.
        text = "open firefox and open kitty and open spotify"   
        parser = self.parser_result(text)
        
        print("\n########### AND connector test ###########")
        self.ast_example(parser)

    # Tests cases where, instead of two commands connected by an AND,
    # there is a single command with a target containing the `and` token.
    # Note: If the next token is an action, the parser will treat it as two separate commands.
    def test_and_in_context(self):
        text = "one, hello, good morning and have a great day"
        parser = self.parser_result(text)
        
        print("\n########### AND in context test ###########")
        self.ast_example(parser)

    def test_clear_target(self):
        text = "open the firefox"
        parser = self.parser_result(text)

        print("\n########### Clear target test ###########")
        self.ast_example(parser)

if __name__ == '__main__':
    unittest.main()
        