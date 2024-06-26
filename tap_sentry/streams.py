"""Stream type classes for tap-sentry."""

from __future__ import annotations

import sys
import typing as t
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qs

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sentry.client import SentryStream

if sys.version_info >= (3, 9):
    pass
else:
    pass


class IssuesStream(SentryStream):
    """Define custom stream."""

    name = "issues"
    path = "/api/0/organizations/{organization_id_or_slug}/issues/"
    primary_keys: t.ClassVar[list[str]] = ["id"]

    schema = th.PropertiesList(
        th.Property("lastSeen", th.DateTimeType),
        th.Property("numComments", th.IntegerType),
        th.Property("userCount", th.IntegerType),
        th.Property("culprit", th.StringType),
        th.Property("title", th.StringType),
        th.Property("id", th.StringType),
        th.Property("assignedTo", th.ObjectType(additional_properties=True)),
        th.Property("logger", th.StringType()),
        th.Property(
            "stats",
            th.ObjectType(additional_properties=True),
        ),
        th.Property("type", th.StringType),
        th.Property("annotations", th.ArrayType(th.StringType)),
        th.Property(
            "metadata",
            th.ObjectType(additional_properties=True),
        ),
        th.Property(
            "status",
            th.StringType(allowed_values=["resolved", "unresolved", "ignored"]),
        ),
        th.Property("subscriptionDetails", th.ObjectType(additional_properties=True)),
        th.Property("isPublic", th.BooleanType),
        th.Property("hasSeen", th.BooleanType),
        th.Property("shortId", th.StringType),
        th.Property("shareId", th.StringType()),
        th.Property("firstSeen", th.StringType),
        th.Property("count", th.StringType),
        th.Property("permalink", th.StringType),
        th.Property("level", th.StringType),
        th.Property("isSubscribed", th.BooleanType),
        th.Property("isBookmarked", th.BooleanType),
        th.Property(
            "project",
            th.ObjectType(
                th.Property("id", th.StringType),
                th.Property("name", th.StringType),
                th.Property("slug", th.StringType),
                additional_properties=True,
            ),
        ),
        th.Property("statusDetails", th.ObjectType(additional_properties=True)),
    ).to_dict()


class EventsStream(SentryStream):
    """Define custom stream."""

    name = "events"
    path = "/api/0/organizations/{organization_id_or_slug}/events/"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    records_jsonpath = "$.data[*]"

    schema = th.PropertiesList(
        th.Property("id", th.StringType()),
        th.Property("raw", th.ObjectType(additional_properties=True)),
        th.Property("timestamp", th.DateTimeType()),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        if next_page_token:
            query_params = parse_qs(next_page_token.query)
            # recreate params dictionary from next url
            return {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        params: dict = {}
        current_hour = datetime.now(tz=timezone.utc).replace(
            minute=0, second=0, microsecond=0
        )
        if not next_page_token:
            # https://docs.sentry.io/concepts/search/searchable-properties/events/
            selected_fields = self.config.get("events:fields") or []
            params["field"] = selected_fields
            if "id" not in selected_fields:
                params["field"].append("id")
            if "timestamp" not in selected_fields:
                params["field"].append("timestamp")
            if "events:query" in self.config:
                params["query"] = self.config.get("events:query")
            params["start"] = (
                self.config.get("events:start_date")
                or (current_hour - timedelta(hours=1)).isoformat()
            )
            params["end"] = (
                self.config.get("events:end_date") or current_hour.isoformat()
            )
            params["sort"] = "-timestamp"
        return params

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Post-process each record returned from the API."""
        return {"id": row.get("id"), "raw": row, "timestamp": row.get("timestamp")}
