__author__ = "Amaury Derigny"
__email__ = "amaury.derigny@smile.fr"
__license__ = "MIT"

__version__ = "0.0.1"

import json

from aws_create_request.app import CreateRequest

def main() -> None:
    create_request = CreateRequest()
    create_request.init_context_request()
    create_request.generate_authorization()
    res_execution = create_request.execute_request()

    response = json.dumps(res_execution.json(), indent=2)

    print(response)
    return response

