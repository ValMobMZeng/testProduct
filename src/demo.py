import functools
from typing import Any

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WireMock:
    def __init__(self, port):
        self.mappings = None
        self.requests = None
        self.count = None
        self.remove_requests = None
        self.find = None

        def generate_functions(url: str) -> Any:
            return type(
                "Requests",
                (),
                {
                    method: functools.partial(
                        getattr(requests, method), url, verify=False
                    )
                    for method in methods
                },
            )

        def build_url(field: str) -> str:
            return f"http://localhost:{port}/__admin/{field}"

        methods = ["get", "post", "put", "delete"]

        actions = {
            "mappings": "mappings",
            "requests": "requests",
            "count": "requests/count",
            "remove_requests": "requests/remove",
            "find": "requests/find",
        }

        for action, mapping in actions.items():
            setattr(self, action, generate_functions(build_url(mapping)))

    def respond_ok(self, url, method, headers=None, response_json=None):
        self.mock_response(
            url,
            method,
            headers,
            response={
                "status": 200,
                "jsonBody": response_json,
                "headers": {"Content-Type": "application/json"},
            },
        )

    def mock_response(self, url, method, headers=None, response=None):
        request = self.build_request(url=url, method=method, headers=headers)
        self.mappings.post(
            json={"request": request, "response": response}
        ).raise_for_status()

    @staticmethod
    def build_request(url, headers, method):
        request = {"method": method}
        if headers is not None:
            request['headers'] = headers
        url_attr = 'urlPattern' if "*" in url else 'url'
        request[url_attr] = url
        return request
