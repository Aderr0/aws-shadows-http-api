
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

        self.canonical_request = None
        self.canonical_request_hash = None


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
    # CREATE CANONICAL REQUEST
    ######################################

    def __create_canonical_request(self) -> str:
        self.canonical_request = CanonicalRequest()
        self.canonical_request.complete_canonical_string()

    def __hash_canonical_request(self) -> str:
        self.canonical_request_hash = self.canonical_request.hash_canonical_request()

    def run(self):
        self.__create_canonical_request()
        self.__hash_canonical_request()

def main() -> None:
    create_request = CreateRequest()
    create_request.init_context_request()
    create_request.run()

def init_logs() -> None:
    list_params = list(filter(lambda argv : "--" in argv or '-', sys.argv))
    try:
        is_log_level_debug = len(list(filter(lambda param : "--debug" in param or "-d" in param, list_params))) > 0
    except Exception:
        is_log_level_debug = False

    logs.set_log_level(is_log_level_debug)



######################################
# CREATE STRING TO SIGN
######################################

def create_string_to_sign(date: str, hashed_canonical_request: str) -> str:
    """
        algorithm
        request_date_time
        credential_scope
        hashed_canonical_request
    """
    algorithm: str = "AWS4-HMAC-SHA256"
    request_date_time: str = date
    credential_scope = f"{date.split('T')[0]}/{REGION}/{SERVICE}/aws4_request"
    hashed_canonical_request = hashed_canonical_request
    string_to_sign = []

    string_to_sign.append(algorithm)
    string_to_sign.append(request_date_time)
    string_to_sign.append(credential_scope)
    string_to_sign.append(hashed_canonical_request)
    
    return "\n".join(string_to_sign)

def extract_date_from_canonical_headers(canonical_headers: list[str]):
    x_amz_date_header = filter(lambda header : header.startswith("x-amz-date"), canonical_headers)
    return list(x_amz_date_header)[0].split(":")[1]


######################################
# CALCULTE SIGNATURE
######################################

def calcuate_signature(date: str, string_to_sign: str) -> str:
    """
        1. kdate
        2. kregion
        3. kservice
        4. ksigning
        5. signature
    """
    k_date = hmac.new(f"AWS4{AWS_SECRET_ACCESS_KEY}".encode("utf-8"), date.split('T')[0].encode("utf-8"), hashlib.sha256).digest()
    k_region = hmac.new(k_date, REGION.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, f"{SERVICE}".encode("utf-8"), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, "aws4_request".encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature


######################################
# AUTHORIZATION HEADER GENERATION
######################################

def extract_credential_scope_from_string_to_sign(string_to_sign: str):
    return string_to_sign.split("\n")[2]

def generate_auth_header(date, signed_headers, signature) -> dict:
    auth_list = ["AWS4-HMAC-SHA256"]
    auth_list.append(f"Credential={AWS_ACCESS_KEY_ID}/{credential_scope}")
    auth_list.append(f"SignedHeaders={signed_headers}")
    auth_list.append(f"Signature={signature}")
    auth = { "Authorization": " ".join(auth_list) }

    return auth


######################################
# MAIN
######################################

if __name__ == "__main__":
    init_logs()
    init_global_vars()
    logs.log_info(f"-- [Version] -- Version <{__version__}>")


    """
        HTTP GET https://endpoint/things/thingName/shadow?name=shadowName
        Request body: (none)

        HTTP POST https://endpoint/things/thingName/shadow?name=shadowName
        Request body: request state document

        HTTP DELETE https://endpoint/things/thingName/shadow?name=shadowName
        Request body: (none)
    """

    ######################################
    # CREATE CANONICAL REQUEST
    ######################################
    step = "Canonical Request Creation"

    http_method = get_http_method()
    canonical_uri = get_canonical_uri()
    canonical_query_string = get_canonical_query_string()
    canonical_headers = get_canonical_headers()
    signed_headers = get_signed_headers(canonical_headers)
    hashed_payload = get_hashed_payload()

    canonical_request = create_canonical_request(http_method, canonical_uri, canonical_query_string, canonical_headers,
        signed_headers, hashed_payload)
    logs.log_debug(step + "\n" + canonical_request + "\n")
    


    ######################################
    # CREATE CANONICAL REQUEST
    ######################################
    step = "Canonical Request Hash"

    hashed_canonical_request = hash_canonical_request(canonical_request)
    logs.log_debug(step + "\n" + hashed_canonical_request + "\n")
    


    ######################################
    # CREATE STRING TO SIGN
    ######################################
    step = "String To Sign Creation"

    date = extract_date_from_canonical_headers(canonical_headers)
    string_to_sign = create_string_to_sign(date, hashed_canonical_request)
    logs.log_debug(step + "\n" + string_to_sign + "\n")



    ######################################
    # CALCULATE SIGNATURE
    ######################################
    step = "Signature calcul"

    signature = calcuate_signature(date, string_to_sign)
    logs.log_debug(step + "\n" + signature + "\n")



    ######################################
    # AUTHORIZATION HEADER GENERATION
    ######################################
    step = "Authorization header generation"

    credential_scope = extract_credential_scope_from_string_to_sign(string_to_sign)
    auth = generate_auth_header(credential_scope, signed_headers, signature)
    logs.log_debug(step + "\n" + str(auth) + "\n")

    host = f"data-ats.iot.{REGION}.amazonaws.com"
    url = f"https://{host}{canonical_uri}"
    auth.update({
        "X-Amz-Date": extract_date_from_canonical_headers(canonical_headers),
    })

    res = requests.request(http_method, url, headers=auth)

    logs.log_info(json.dumps(json.loads(res.text), indent=4))