import unittest
import datetime

from aws_create_request.canonical_request import CanonicalRequest
from aws_create_request.constants import HTTPMethod

class TestCanonicalRequest(unittest.TestCase):

    def test_constructor(self):
        """
        Can create a CanonicalRequest object
        """
        msg = f"Should be an instance of {CanonicalRequest.__name__} with empty attributes"

        test = CanonicalRequest()

        self.assertIsInstance(test, CanonicalRequest, msg)


    def test_shadow_method_get(self):
        """
        Can initialize the shadow method attributes of a CanonicalRequest object at get 
        """
        msg = f"Should set the http method from shadow method"

        method = "get"

        test = CanonicalRequest()
        test.complete_canonical_request(
            shadow_method=method,
            thing_name="",
            shadow_name="",
            region="",
            payload=""
        )

        self.assertEqual(test.http_method, getattr(HTTPMethod, method.upper()), msg)

    def test_shadow_method_update(self):
        """
        Can initialize the shadow method attributes of a CanonicalRequest object at update 
        """
        msg = f"Should set the http method from shadow method"

        method = "update"

        test = CanonicalRequest()
        test.complete_canonical_request(
            shadow_method=method,
            thing_name="",
            shadow_name="",
            region="",
            payload=""
        )

        self.assertEqual(test.http_method, getattr(HTTPMethod, method.upper()), msg)

    def test_shadow_method_delete(self):
        """
        Can initialize the shadow method attributes of a CanonicalRequest object at delete 
        """
        msg = f"Should set the http method from shadow method"

        method = "delete"

        test = CanonicalRequest()
        test.complete_canonical_request(
            shadow_method=method,
            thing_name="",
            shadow_name="",
            region="",
            payload=""
        )

        self.assertEqual(test.http_method, getattr(HTTPMethod, method.upper()), msg)

    def test_shadow_method_random(self):
        """
        Can't initialize the shadow method attributes of a CanonicalRequest object at another value 
        """
        msg = f"Should raise an SystemExit exception"

        method = "random_value"

        test = CanonicalRequest()

        with self.assertRaises(SystemExit, msg=msg):
            test.complete_canonical_request(
                shadow_method=method,
                thing_name="",
                shadow_name="",
                region="",
                payload=""
            )

    def test_shadow_method_empty(self):
        """
        Can't initialize the shadow method attributes of a CanonicalRequest object at nothing 
        """
        msg = f"Should raise an SystemExit exception"

        method = ""

        test = CanonicalRequest()

        with self.assertRaises(SystemExit, msg=msg):
            test.complete_canonical_request(
                shadow_method=method,
                thing_name="",
                shadow_name="",
                region="",
                payload=""
            )
        

    def test_canonical_uri_with_random_thing_name(self):
        """
        Can initialize the canonical uri of a CanonicalRequest object with a random thing name 
        """
        msg = f"Should initialize the canonical uri"

        method = "get"
        thing_name = "my-thing-name"

        expected_result = f"/things/{thing_name}/shadow"

        test = CanonicalRequest()
        test.complete_canonical_request(
            shadow_method=method,
            thing_name=thing_name,
            shadow_name="",
            region="",
            payload=""
        )

        self.assertEqual(test.canonical_uri, expected_result, msg)


    def test_canonical_query_string_with_shadow_name(self):
        """
        Can's initialize the canonical query string of a CanonicalRequest object with random shadow name 
        """
        msg = f"Should initialize the canonical query string"

        method = "get"
        thing_name = "my-thing-name"
        shadow_name = "my-shadow-name"

        expected_result = f"name={shadow_name}"

        test = CanonicalRequest()   
        test.complete_canonical_request(
            shadow_method=method,
            thing_name=thing_name,
            shadow_name=shadow_name,
            region="",
            payload=""
        )

        self.assertEqual(test.canonical_query_string, expected_result, msg)

    def test_canonical_query_string_without_shadow_name(self):
        """
        Can't initialize the canonical query string of a CanonicalRequest object without shadow name 
        """
        msg = f"Should initialize the canonical query string"

        method = "get"
        thing_name = "my-thing-name"
        shadow_name = None

        expected_result = ""

        test = CanonicalRequest()   
        test.complete_canonical_request(
            shadow_method=method,
            thing_name=thing_name,
            shadow_name=shadow_name,
            region="",
            payload=""
        )

        self.assertEqual(test.canonical_query_string, expected_result, msg)


    def test_canonical_headers_type(self):
        """
        Can initialize the canonical headers of a CanonicalRequest object
        """
        msg = f"Should initialize the canonical headers as list of string with a minimum length of 2"

        method = "get"
        thing_name = "my-thing-name"
        shadow_name = None
        region = "eu-west-1"

        substring_host = "host"
        substring_date = "x-amz-date"

        excepected_result = 2

        test = CanonicalRequest()   
        test.complete_canonical_request(
            shadow_method=method,
            thing_name=thing_name,
            shadow_name=shadow_name,
            region=region,
            payload=""
        )

        self.assertIsInstance(test.canonical_headers, list, msg)
        self.assertGreaterEqual(len(test.canonical_headers), excepected_result, msg)

    def test_canonical_headers_required_values(self):
        """
        Can initialize the required headers in the canonical headers of a CanonicalRequest object
        """
        msg = f"Should initialize the 'host' and 'x-amz-date' headers"

        method = "get"
        thing_name = "my-thing-name"
        shadow_name = None
        region = "eu-west-1"

        substring_host = "host"
        substring_date = "x-amz-date"

        expected_host_header = f"data-ats.iot.{region}.amazonaws.com"
        expected_date_header_format = "%Y%m%dT%H%M%SZ"

        test = CanonicalRequest()   
        test.complete_canonical_request(
            shadow_method=method,
            thing_name=thing_name,
            shadow_name=shadow_name,
            region=region,
            payload=""
        )
        
        host_header = list(filter(lambda header : substring_host in header , test.canonical_headers))
        self.assertEqual(len(host_header), 1, msg="Should find a host header")
        host_header_value = host_header[0].split(":")[1]
        self.assertEqual(host_header_value, expected_host_header, msg)

        

        date_header = list(filter(lambda header : substring_date in header , test.canonical_headers))
        self.assertEqual(len(date_header), 1, msg="Should find a date header")
        date_header_value = date_header[0].split(":")[1]
        self.assertEqual(
            date_header_value, 
            datetime.datetime
                .strptime(date_header_value, expected_date_header_format)
                .strftime(expected_date_header_format), 
            msg
        )


    




if __name__.__eq__("__main__"):
    unittest.main()
    print("All tests passed successfully")