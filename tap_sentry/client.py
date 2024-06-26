"""REST client handling, including sentryStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, HeaderLinkPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 9):
    pass
else:
    pass

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]


class SentryHeaderLinkPaginator(HeaderLinkPaginator):
    """Pagination helper for Sentry API."""

    def has_more(self, response: requests.Response) -> bool:
        """Return True if there are more pages to paginate."""
        results: str | None = response.links.get("next", {}).get("results")
        return results == "true"


class SentryStream(RESTStream):
    """sentry stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("api_url", "https://sentry.io")

    records_jsonpath = "$[*]"  # Or override `parse_response`.

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("auth_token"),
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")  # noqa: ERA001
        return headers

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        If the source API can make use of the `next_page_token_jsonpath`
        attribute, or it contains a `X-Next-Page` header in the response
        then you can remove this method.

        If you need custom pagination that uses page numbers, "next" links, or
        other approaches, please read the guide: https://sdk.meltano.com/en/v0.25.0/guides/pagination-classes.html.

        Returns:
            A pagination helper instance.
        """
        return SentryHeaderLinkPaginator()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ARG002, ANN401
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())
