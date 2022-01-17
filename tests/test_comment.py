import unittest
from app.models import Comments

class CommentsTest(unittest.TestCase):
    def setUp(self):
        self.new_comment = Comments(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", 
        )

    def test_instance(self):
        self.assertTrue(isinstance(self.new_comment, Comments))

if __name__ == "__main__":
    unittest.main()