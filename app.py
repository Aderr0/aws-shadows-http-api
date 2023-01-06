
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

SERVICE = ""

THING_NAME = ""
REGION = ""
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

parser = argparse.ArgumentParser("ShadowHttpApi", description="Manipulating AWS shadow using HTTP API and only natives python's modules")
parser.add_argument("-t", "--thing-name", required=True)
parser.add_argument("-r", "--region", default="eu-west-1", required=False)
parser.add_argument("-a", "--aws-access-key-id", required=True)
parser.add_argument("-s", "--aws-secret-access-key", required=True)

def init_logs() -> None:
    list_params = list(filter(lambda argv : "--" in argv or '-', sys.argv))
    try:
        is_log_level_debug = len(list(filter(lambda param : "--debug" in param or "-d" in param, list_params))) > 0
    except Exception:
        is_log_level_debug = False

    logs.set_log_level(is_log_level_debug)

def init_global_vars():
    global SERVICE, THING_NAME, REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    args = parser.parse_args()

    SERVICE = "iotdata"

    print(args)

    THING_NAME = args.thing_name
    REGION = args.region
    AWS_ACCESS_KEY_ID = args.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = args.aws_secret_access_key



######################################
# CREATE CANONICAL REQUEST
######################################

def create_canonical_request(http_method: str, canonical_uri: str, canonical_query_string: str, canonical_headers: list[str], 
        signed_headers: str, hashed_payload: str) -> str:
    """
        http_method 
        canonical_uri
        canonical_query_string
        canonical_headers
        signed_headers
        hashed_payload
    """
    canonical_request = [http_method]
    canonical_request.append(canonical_uri)
    canonical_request.append(canonical_query_string)
    canonical_request.extend(canonical_headers)
    canonical_request.append(signed_headers)
    canonical_request.append(hashed_payload)
    return "\n".join(canonical_request)

def get_http_method() -> str:
    # TODO
    http_method: str = "GET"
    return http_method.upper()

def get_canonical_uri() -> str:
    # TODO
    uri: str = f"/things/{THING_NAME}/shadow"
    return uri

def get_canonical_query_string() -> str:
    # TODO is shadow named ?
    query_string = ""
    is_shadow_named = False

    if is_shadow_named:
        shadow_name: str = ""
        query_string = f"?name={shadow_name}"
    return query_string

def get_canonical_headers() -> list[str]:
    host: str = f"host:data-ats.iot.{REGION}.amazonaws.com"
    date: str = f"x-amz-date:{datetime.datetime.now(tz=pytz.timezone('UTC')).strftime('%Y%m%dT%H%M%SZ')}"
    # content_type: str = "application/json"

    headers: list[str] = [host, date]
    headers.sort()
    headers.append("")

    return headers

def get_signed_headers(canonical_headers: list[str]) -> str:
    signed_headers: list[str] = []
    canonical_headers_filter = filter(lambda header : header.startswith(("x-amz", "host")), canonical_headers)
    for header in list(canonical_headers_filter):
        if len(header.split(":")) > 0:
            signed_headers.append(header.split(":")[0])
        
    return ";".join(signed_headers)

def get_hashed_payload() -> str:
    # TODO get payload
    payload: str = ""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


######################################
# HASH CANONICAL REQUEST
######################################

def hash_canonical_request(canonical_request: str) -> str:
    return hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()


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