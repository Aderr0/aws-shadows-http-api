
import sys
import datetime
import pytz
import hashlib

from aws_create_request.constants import HTTPMethod

class CanonicalRequest:
    """
        http_method 
        canonical_uri
        canonical_query_string
        canonical_headers
        signed_headers
        hashed_payload
    """

    def __init__(self) -> None:
        self.http_method: str = ""
        self.canonical_uri: str = ""
        self.canonical_query_string: str = ""
        self.canonical_headers: list[str] = []
        self.signed_headers: str = ""
        self.hashed_payload: str = ""

    def get_date_from_canonical_headers(self) -> str:
        try:
            x_amz_date_header = filter(lambda header : header.startswith("x-amz-date"), self.canonical_headers)
            date = list(x_amz_date_header)[0].split(":")[1]
        except Exception:
            date = ""
        return date

    def complete_canonical_request(self, shadow_method: str, thing_name: str, shadow_name: str | None, region: str, payload: str):
        self.__set_http_method(shadow_method)
        self.__set_canonical_uri(thing_name)
        self.__set_canonical_query_string(shadow_name)
        self.__set_canonical_headers(region)
        self.__set_signed_headers()
        self.__set_hashed_payload(payload)

    def __set_http_method(self, shadow_method: str) -> None:
        try:
            self.http_method = getattr(HTTPMethod, shadow_method.upper())
        except AttributeError as a_err:
            sys.exit(a_err)

    def __set_canonical_uri(self, thing_name: str) -> None:
        self.canonical_uri = f"/things/{thing_name}/shadow"

    def __set_canonical_query_string(self, shadow_name: str | None) -> None:
        query_string = ""

        if shadow_name is not None:
            query_string = f"name={shadow_name}"

        self.canonical_query_string = query_string

    def __set_canonical_headers(self, region: str) -> None:
        host: str = f"host:data-ats.iot.{region}.amazonaws.com"
        date: str = f"x-amz-date:{datetime.datetime.now(tz=pytz.timezone('UTC')).strftime('%Y%m%dT%H%M%SZ')}"
        # content_type: str = "application/json"

        headers: list[str] = [host, date]
        headers.sort()
        headers.append("")

        self.canonical_headers = headers

    def __set_signed_headers(self) -> str:
        signed_headers: list[str] = []
        canonical_headers_filter = filter(lambda header : header.startswith(("x-amz", "host")), self.canonical_headers)
        for header in list(canonical_headers_filter):
            if len(header.split(":")) > 0:
                signed_headers.append(header.split(":")[0])
            
        self.signed_headers = ";".join(signed_headers)

    def __set_hashed_payload(self, payload: str) -> str:
        self.hashed_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()


    def hash_canonical_request(self) -> str:
        canonical_string = self.__generate_canonical_string()
        return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()

    def __generate_canonical_string(self) -> str:
        canonical_list = [self.http_method]
        canonical_list.append(self.canonical_uri)
        canonical_list.append(self.canonical_query_string)
        canonical_list.extend(self.canonical_headers)
        canonical_list.append(self.signed_headers)
        canonical_list.append(self.hashed_payload)

        return "\n".join(canonical_list)
    
