"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_sentry.tap import Tapsentry

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    # TODO(dejii): Initialize minimal tap config # noqa: FIX002, TD003
}


# Run standard built-in tap tests from the SDK:
TestTapsentry = get_tap_test_class(
    tap_class=Tapsentry,
    config=SAMPLE_CONFIG,
)


# TODO(dejii): Create additional tests as appropriate. # noqa: FIX002, TD003
