
import hmac
import hashlib

from canonical_request import CanonicalRequest

class StringToSign:
    """
        algorithm
        request_date_time
        credential_scope
        hashed_canonical_request
    """

    def __init__(self) -> None:
        self.algorithm: str = ""
        self.request_date_time: str = ""
        self.credential_scope: str = ""
        self.hashed_canonical_request: str = ""
        pass

    def complete_string_to_sign(self, canonical_request: CanonicalRequest, canonical_request_hash: str, region: str, service: str) -> None:
        self.__set_algorithm()
        self.__set_request_date_time(canonical_request)
        self.__set_credential_scope(region, service)
        self.__set_hashed_canonical_request(canonical_request_hash)

    def __set_algorithm(self) -> None:
        self.algorithm = "AWS4-HMAC-SHA256"

    def __set_request_date_time(self, canonical_request: CanonicalRequest) -> None:
        self.request_date_time = canonical_request.get_date_from_canonical_headers()

    def __set_credential_scope(self, region: str, service: str) -> None:
        self.credential_scope = f"{self.request_date_time.split('T')[0]}/{region}/{service}/aws4_request"

    def __set_hashed_canonical_request(self, canonical_request_hash: str) -> None:
        self.hashed_canonical_request = canonical_request_hash


    def __generate_string_to_sign(self) -> str:
        string_to_sign_list = [self.algorithm]
        string_to_sign_list.append(self.request_date_time)
        string_to_sign_list.append(self.credential_scope)
        string_to_sign_list.append(self.hashed_canonical_request)

        return "\n".join(string_to_sign_list)

    def __sign(self, key: bytes, data: bytes, is_signature=False) -> bytes | str:
        hash = hmac.new(key, data, hashlib.sha256)
        return hash.hexdigest() if is_signature else hash.digest()

    def calculate_signature(self, aws_secret_access_key: str) -> str:
        """
            1. kdate
            2. kregion
            3. kservice
            4. ksigning
            5. signature
        """
        string_to_sign = self.__generate_string_to_sign()
        [d_date, d_region, d_service, d_signing] = self.credential_scope.split("/")

        k_date = self.__sign(f"AWS4{aws_secret_access_key}".encode("utf-8"), d_date.encode("utf-8"))
        k_region = self.__sign(k_date, d_region.encode("utf-8"))
        k_service = self.__sign(k_region, d_service.encode("utf-8"))
        k_signing = self.__sign(k_service, d_signing.encode("utf-8"))
        signature = self.__sign(k_signing, string_to_sign.encode("utf-8"), is_signature=True)

        return signature