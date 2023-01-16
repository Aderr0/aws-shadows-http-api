__author__ = "Amaury Derigny"
__email__ = "amaury.derigny@smile.fr"
__license__ = "MIT"

__version__ = "0.0.1"

from aws_create_request.app import get_response_from_request

def main() -> dict:
    return get_response_from_request()
