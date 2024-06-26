"""sentry tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_sentry import streams


class Tapsentry(Tap):
    """sentry tap class."""

    name = "tap-sentry"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            secret=True,
            description="The token to authenticate against the API service. https://docs.sentry.io/api/auth/",
        ),
        th.Property(
            "organization_id_or_slug",
            th.StringType,
            description="The ID or slug of the organization the resource belongs to.",
        ),
        th.Property(
            "query",
            th.DateTimeType,
            description="""An optional Sentry structured search query.
              If not provided an implied "is:unresolved" is assumed.""",
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://sentry.io",
            description="The url for the Sentry API service",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.SentryStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.EventsStream(self),
        ]


if __name__ == "__main__":
    Tapsentry.cli()
