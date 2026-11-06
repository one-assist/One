
"""
The parser is where the distinction is made between elements conveying an intended action and those that merely complement the sentence 
(such as *and*, *in*, *to*, *on*). Furthermore, the command is separated into a target and an action.
"""

from src.lexer.token import Token, TokenType
from src.classifier.model import *

class CommandExpr:
        pass

class SingleAction(CommandExpr):
    def __init__(self, intent: str | None):
        self.intent: str | None = intent

class SequenceAction(CommandExpr):
    def __init__(self, left: CommandExpr, operator: str, right: CommandExpr):
        self.left: CommandExpr = left
        self.operator: str = operator
        self.right: CommandExpr = right

class Parser:
    def __init__(self, tokens: list[Token], intent: str | None):
        self.tokens: list[Token] = tokens
        self.current_token: int = 0
        self.intent: str | None = intent

    def peek(self) -> Token:
        return self.tokens[self.current_token]
    
    def advance(self):
        self.current_token += 1

    def previous(self) -> Token:
        return self.tokens[self.current_token - 1]
        
    #Is similar to match, but does not advance the token if it does not match
    def check(self, token_type: str) -> bool:
        if self.current_token >= len(self.tokens):
            return False
        return self.peek().type == token_type

    # if the current token matches the given type, advance and return True, otherwise return False
    def match(self, token_type: str) -> bool:
        if self.check(token_type):
            self.advance()
            return True
        return False

    def parse(self):
        buffer: list[str] = []

        while self.current_token < len(self.tokens) and not self.check("and"):
            buffer.append(self.peek().lexeme)
            self.advance()
            
        return buffer

    def parse_command(self) -> CommandExpr:
        buffer = self.parse()
        text = " ".join(buffer)
        first_intent = Classifier().get_intent(text).intent

        if first_intent == "UNKNOWN":
            first_intent = self.intent

        while self.match("and"):
            operator = self.previous().lexeme
            position = self.current_token

            buffer = self.parse()
            text = " ".join(buffer)
            intent_object = Classifier().get_intent(text)

            if intent_object.intent != "UNKNOWN":
                self.intent = intent_object.intent
                self.current_token = position

                left = SingleAction(first_intent)
                right = self.parse_command()

                return SequenceAction(left, operator, right)

        return SingleAction(first_intent)