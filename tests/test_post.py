import imp
from re import I
import unittest
from app.models import Posts

class PitchTest(unittest.TestCase):
    def setUp(self):
        self.new_post = Posts(
            "Lorem ipsum.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Fintech"
        )

    def test_instance(self):
        self.assertTrue(isinstance(self.new_post, Posts))

if __name__ == "__main__":
    unittest.main()