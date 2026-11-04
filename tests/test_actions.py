"""Tests command execution without requiring microphone input or external services."""

import unittest
from unittest.mock import Mock, patch

from src.ast.checker import ast_checker
from src.classifier.model import Classifier
from src.lexer.scanner import Scanner
from src.parser.parser import Parser


class TestActions(unittest.TestCase):
    @patch("src.commands.actions.history_insert")
    @patch("src.commands.actions.speech")
    @patch("src.commands.actions.create_task")
    @patch(
        "src.commands.actions.ask_user",
        side_effect=[
            "make a cake",
            "in five days",
            "pending",
            "buy ingredients",
        ],
    )
    def test_create_task_command(
        self,
        ask_user: Mock,
        create_task: Mock,
        _speech: Mock,
        history_insert: Mock,
    ) -> None:
        command = "create task"
        intent = Classifier().get_intent(command).intent
        self.assertEqual(intent, "ADD_TASK")

        scanner = Scanner(command)
        scanner.scan()
        ast_root = Parser(scanner.tokens, intent).parse_command()

        ast_checker(ast_root)

        self.assertEqual(ask_user.call_count, 4)
        create_task.assert_called_once()
        self.assertEqual(create_task.call_args.args[0], "make a cake")
        self.assertEqual(create_task.call_args.args[2], "pending")
        self.assertEqual(create_task.call_args.args[3], "buy ingredients")
        history_insert.assert_called_once_with("ADD_TASK", "make a cake")


if __name__ == "__main__":
    unittest.main()
