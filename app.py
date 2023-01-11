
import sys
import datetime
import hashlib
import hmac
import requests
import pytz
import argparse
import json

import logs as logs 
from __init__ import __version__
from canonical_request import CanonicalRequest
from string_to_sign import StringToSign



"""
    HTTP GET https://endpoint/things/thingName/shadow?name=shadowName
    Request body: (none)

    HTTP POST https://endpoint/things/thingName/shadow?name=shadowName
    Request body: request state document

    HTTP DELETE https://endpoint/things/thingName/shadow?name=shadowName
    Request body: (none)
"""   

class Credentials:
    def __init__(self, aws_access_key_id = "", aws_secret_access_key = "") -> None:
        self.aws_access_key_id: str = aws_access_key_id
        self.aws_secret_access_key: str = aws_secret_access_key

    def get_aws_access_key_id(self) -> str:
        return self.aws_access_key_id

    def get_aws_secret_access_key(self) -> str:
        return self.aws_secret_access_key

    def set_credentials(self, aws_access_key_id, aws_secret_access_key) -> None:
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

class CreateRequest:
    """Class to generate http request with authorization header"""

    def __init__(self) -> None:
        self.service: str = "iotdata"

        self.thing_name: str = ""
        self.region: str = ""
        self.credentials: Credentials = Credentials()

        # TODO Set those three variables dynamically
        self.http_method: str = "GET"
        self.shadow_name: str | None = None
        self.payload: str = ""

        self.canonical_request = None
        self.canonical_request_hash = None
        self.string_to_sign = None
        self.signature = None
        self.authorization = None



    ######################################
    # INIT CONTEXT REQUEST
    ######################################

    def __parser_cmd_line(self) -> dict:
        parser = self.__init_argparse()
        args = parser.parse_args()
        return args

    def __init_argparse(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            "ShadowHttpApi", 
            description="Manipulating AWS shadow using HTTP API and only natives python's modules",
            add_help=True
        )
        
        parser.add_argument(
            "-t", 
            "--thing-name", 
            help="The name of the thing in AWS",
            required=True)

        parser.add_argument(
            "-r", 
            "--region", 
            default="eu-west-1", 
            help="The region where the thing is register in AWS. Default to 'eu-west-1'",
            required=False
        )

        parser.add_argument(
            "-a", 
            "--aws-access-key-id", 
            help="AWS access key id that you can find in ~/.aws/credentials",
            required=True
        )
        
        parser.add_argument(
            "-s", 
            "--aws-secret-access-key", 
            help="AWS secret access key that you can find in ~/.aws/credentials",
            required=True)

        return parser

    def __init_parameters(self, args) -> None:
        # Required
        try:
            self.thing_name = args.thing_name
            self.credentials.set_credentials(aws_access_key_id=args.aws_access_key_id, aws_secret_access_key=args.aws_secret_access_key)
        except Exception as e:
            sys.exit(e)

        # Not Required
        if args.region:
            self.region = args.region

    def init_context_request(self) -> None:
        args = self.__parser_cmd_line()
        self.__init_parameters(args)



    ######################################
    # GENERATION AUTHORIZATION
    ######################################

    def __create_canonical_request(self) -> None:
        self.canonical_request = CanonicalRequest()
        self.canonical_request.complete_canonical_request(
            http_method="GET",
            thing_name=self.thing_name,
            shadow_name=self.shadow_name,
            region=self.region,
            payload=self.payload
        )

    def __hash_canonical_request(self) -> None:
        self.canonical_request_hash = self.canonical_request.hash_canonical_request()

    def __create_string_to_sign(self) -> None:
        self.string_to_sign = StringToSign()
        self.string_to_sign.complete_string_to_sign(
            canonical_request=self.canonical_request,
            canonical_request_hash=self.canonical_request_hash,
            region=self.region,
            service=self.service
        )

    def __calculate_signature(self) -> None:
        self.signature = self.string_to_sign.calculate_signature(self.credentials.aws_secret_access_key)

    def __generate_authorization_header(self) -> None:
        auth_list = ["AWS4-HMAC-SHA256"]
        auth_list.append(f"Credential={self.credentials.aws_access_key_id}/{self.string_to_sign.credential_scope}")
        auth_list.append(f"SignedHeaders={self.canonical_request.signed_headers}")
        auth_list.append(f"Signature={self.signature}")

        self.authorization = { "Authorization": " ".join(auth_list) }

    def generate_authorization(self):
        self.__create_canonical_request()
        self.__hash_canonical_request()
        self.__create_string_to_sign()
        self.__calculate_signature()
        self.__generate_authorization_header()



    ######################################
    # EXECUTE REQUEST
    ######################################

    def execute_request(self):
        host = f"data-ats.iot.{self.region}.amazonaws.com"
        url = f"https://{host}{self.canonical_request.canonical_uri}"

        if len(self.canonical_request.canonical_query_string) > 0:
            url = f"{url}?{self.canonical_request.canonical_query_string}"

        headers = self.authorization
        headers.update({
            "X-Amz-Date": self.string_to_sign.request_date_time,
        })

        res = requests.request(self.http_method, url, headers=auth)

        print(res)

def main() -> None:
    create_request = CreateRequest()
    create_request.init_context_request()
    create_request.generate_authorization()
    create_request.execute_request()



# def init_logs() -> None:
#     list_params = list(filter(lambda argv : "--" in argv or '-', sys.argv))
#     try:
#         is_log_level_debug = len(list(filter(lambda param : "--debug" in param or "-d" in param, list_params))) > 0
#     except Exception:
#         is_log_level_debug = False

#     logs.set_log_level(is_log_level_debug)
