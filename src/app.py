#!/usr/bin/env python3

import sys
import requests
import argparse
import json
import os

from __init__ import __version__
from canonical_request import CanonicalRequest
from string_to_sign import StringToSign
from constants import HTTPMethod, AVAILABLE_REGION


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
        self.shadow_method: str = ""
        self.credentials: Credentials = Credentials()
        self.payload: str = ""
        self.shadow_name: str | None = None

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
            dest="thing_name",
            help="The name of the thing in AWS",
            required=True
        )
        
        parser.add_argument(
            "-m", 
            "--method", 
            dest="method",
            help="The shadow method. It is can be either GET, DELETE and UPDATE.",
            required=True
        )

        parser.add_argument(
            "-s", 
            "--shadow-name", 
            dest="shadow_name",
            help="Path to the shadow request state document. Required only if shadow method is update.",
            required=False
        )

        parser.add_argument(
            "-d", 
            "--state-document", 
            dest="state_document",
            help="Path to the shadow request state document. Required only if shadow method is update.",
            required=False
        )

        parser.add_argument(
            "-r", 
            "--region", 
            default="eu-west-1",
            dest="region",
            help="The region where the thing is register in AWS. Default to 'eu-west-1'",
            required=False
        )

        parser.add_argument(
            "-a", 
            "--aws-access-key-id", 
            dest="aws_access_key_id",
            help="AWS access key id that you can find in ~/.aws/credentials",
            required=True
        )
        
        parser.add_argument(
            "-k", 
            "--aws-secret-access-key", 
            dest="aws_secret_access_key",
            help="AWS secret access key that you can find in ~/.aws/credentials",
            required=True
        )

        return parser

    def __init_parameters(self, args) -> None:
        # Required
        try:
            self.thing_name = args.thing_name
            self.shadow_method = args.method
            self.credentials.set_credentials(aws_access_key_id=args.aws_access_key_id, aws_secret_access_key=args.aws_secret_access_key)
        except Exception as e:
            sys.exit(e)

        # Not Required
        if args.region:
            if args.region not in AVAILABLE_REGION:
                sys.exit(f"'{args.region}' is not an available region.\n" +
                    "See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html " +
                    "for availables regions"
                )
            else:
                self.region = args.region
        if args.shadow_name:
            self.shadow_name = args.shadow_name
        
        try:
            if getattr(HTTPMethod, self.shadow_method.upper()) == HTTPMethod.UPDATE:
                if args.state_document:
                    self.payload = self.__get_payload_from_state_document(args.state_document)
                else:
                    raise argparse.ArgumentError("Argument missing", "With an UPDATE shadow method, a path to the state document have to be passed")
        except AttributeError as a_err:
            sys.exit(a_err)
        except Exception as e:
            sys.exit(e)

    def __get_payload_from_state_document(self, state_document_path):
        if not os.path.exists(state_document_path):
            raise FileExistsError(f"Path {state_document_path} does not exist")
        else:
            try:
                with open(state_document_path) as state_document:
                    state_document_content: str = str(json.load(state_document)).replace("'", "\"")
                    return state_document_content
            except Exception:
                raise Exception("Error while reading request state document")

    def init_context_request(self) -> None:
        args = self.__parser_cmd_line()
        self.__init_parameters(args)



    ######################################
    # GENERATION AUTHORIZATION
    ######################################

    def __create_canonical_request(self) -> None:
        self.canonical_request = CanonicalRequest()
        self.canonical_request.complete_canonical_request(
            shadow_method=self.shadow_method,
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

    def execute_request(self) -> requests.Response:
        host = f"data-ats.iot.{self.region}.amazonaws.com"
        url = f"https://{host}{self.canonical_request.canonical_uri}"

        if len(self.canonical_request.canonical_query_string) > 0:
            url = f"{url}?{self.canonical_request.canonical_query_string}"

        headers = self.authorization
        headers.update({
            "X-Amz-Date": self.string_to_sign.request_date_time,
            "Content-Length": str(len(self.payload))
        })

        return requests.request(self.canonical_request.http_method, url, headers=headers, data=self.payload)

def main() -> None:
    create_request = CreateRequest()
    create_request.init_context_request()
    create_request.generate_authorization()
    response = create_request.execute_request()

    print(json.dumps(response.json(), indent=2))

if __name__.__eq__("__main__"):
    main()


