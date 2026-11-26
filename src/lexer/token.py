"""
Where it is defined which words will be tokens.
"""

from dataclasses import dataclass
from enum import StrEnum


#the actions tokens
class TokenType(StrEnum):
    AND = "and"
    IDENTIFIER = "identifier"

@dataclass
class Token:
    type: TokenType
    lexeme: str
    
