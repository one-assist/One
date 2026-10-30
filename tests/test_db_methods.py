"""
Test database auxiliary methods
"""

import unittest
from typing import override

from database.methods import DbMethods


class TestDatabaseMethods(unittest.TestCase):
    db_methods: DbMethods | None = None

    @override
    def setUp(self) -> None:
        self.db_methods = DbMethods()
        
    def test_formal_date(self):
        db_methods = self.db_methods
        assert db_methods is not None
        result = db_methods.formatDate("in 10 days at 1:50 pm")
    
        if result is None:
            self.fail("formatDate returned None for a valid date string.")
            
        print(f"Format date returned: {result}")

if __name__ == '__main__':
    unittest.main()