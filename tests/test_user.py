import unittest
from app.models import User

class UserTest(unittest.TestCase):
    def setUp(self):
        self.new_user = User(
            "John", 
            "Snow", 
            "johnsnow@gmail.com", 
            "johnsnow123456789", 
            False
        )

    def test_instance(self):
        self.assertTrue(isinstance(self.new_user, User))

if __name__ == "__main__":
    unittest.main()