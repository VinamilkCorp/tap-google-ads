#!/usr/bin/env python3
import logging
import singer
import os
from singer import utils
from tap_google_ads.discover import create_resource_schema
from tap_google_ads.discover import do_discover
from tap_google_ads.sync import do_sync


LOGGER = singer.get_logger()


REQUIRED_CONFIG_KEYS = [
    "start_date",
    "oauth_client_id",
    "oauth_client_secret",
    "refresh_token",
    "login_customer_ids",
    "developer_token",
]


def main_impl_without_ssl():
    with singer.utils.no_ssl_verification():
        main_impl()


def main_impl():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    resource_schema = create_resource_schema(args.config)
    state = {}

    if args.state:
        state.update(args.state)
    if args.discover:
        do_discover(resource_schema)
        LOGGER.info("Discovery complete")
    elif args.catalog:
        do_sync(args.config, args.catalog.to_dict(), resource_schema, state)
        LOGGER.info("Sync Completed")
    else:
        LOGGER.info("No properties were selected")


def main():
    google_logger = logging.getLogger("google")
    google_logger.setLevel(level=logging.CRITICAL)

    try:
        if os.environ.get("NO_SSL", False):
            main_impl_without_ssl()
        else:
            main_impl()
    except Exception as e:
        for line in str(e).splitlines():
            LOGGER.critical(line)
        raise e


if __name__ == "__main__":
    main()
