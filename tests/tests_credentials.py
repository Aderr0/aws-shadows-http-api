import unittest

from aws_create_request.app import Credentials

class TestCredentials(unittest.TestCase):

    def test_constructor(self):
        """
        Test that it can create a Credentials object
        """
        data = None
        espected_result = Credentials.__name__
        result = Credentials()

        self.assertEqual(result, espected_result)



if __name__.__eq__("__main__"):

    unittest.main()
    print("All tests passed successfully")