import unittest

from aws_create_request.app import Credentials

class TestCredentials(unittest.TestCase):

    def test_empty_constructor(self):
        """
        Can create a Credentials object without parameters
        """
        msg = f"Should be an instance of {Credentials.__name__} with empty attributes"

        test = Credentials()

        self.assertIsInstance(test, Credentials, msg)
        self.assertEqual(test.get_aws_access_key_id(), "", msg)
        self.assertEqual(test.get_aws_secret_access_key(), "", msg)

    def test_complete_constructor(self):
        """
        Can create a Credentials object
        """
        msg = f"Should be an instance of {Credentials.__name__} with defined attributes"
        
        aws_access_key_id = "my_aws_access_key_id"
        aws_secret_access_key = "my_aws_secret_access_key"

        test = Credentials(aws_access_key_id, aws_secret_access_key)

        self.assertIsInstance(test, Credentials, msg)
        self.assertEqual(test.get_aws_access_key_id(), aws_access_key_id, msg)
        self.assertEqual(test.get_aws_secret_access_key(), aws_secret_access_key, msg)

    def test_set_credentials(self):
        """
        Can set credentials to a Credential object
        """
        msg = f"Should change the attributes"
        
        aws_access_key_id = "my_aws_access_key_id"
        aws_secret_access_key = "my_aws_secret_access_key"

        test = Credentials()
        test.set_credentials(aws_access_key_id, aws_secret_access_key)

        self.assertEqual(test.get_aws_access_key_id(), aws_access_key_id, msg)
        self.assertEqual(test.get_aws_secret_access_key(), aws_secret_access_key, msg)



if __name__.__eq__("__main__"):
    unittest.main()
    print("All tests passed successfully")