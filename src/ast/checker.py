
"""
The AST checks if it is a SequenceActions; if so, it checks the left and right nodes.
If it is a SingleActions, it forwards it to the Actions class.
"""
from src.parser.parser import *
from src.commands.actions import *

command_execute = Actions()

#if it is a SequenceAction, check the left and right nodes
def ast_checker(node: CommandExpr):
    
    if isinstance(node, SequenceAction):
        ast_checker(node.left)
        ast_checker(node.right)

    if isinstance(node, SingleAction) and node.intent:
        command_execute.process(node.intent)
        