#!/usr/bin/env python
from .session import Session
from .cdx import search
from .settings import DEFAULT_USER_AGENT, DEFAULT_ROOT
import logging

ARCHIVE_TEMPLATE = "https://web.archive.org/web/{timestamp}/{url}"

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("url",
        help="The URL of the resource you want to download.")

    parser.add_argument("--from-date",
        help="Timestamp-string indicating the earliest snapshot to download. Should take the format YYYYMMDDhhss, though you can omit as many of the trailing digits as you like. E.g., '201501' is valid.")

    parser.add_argument("--to-date",
        help="Timestamp-string indicating the latest snapshot to download. Should take the format YYYYMMDDhhss, though you can omit as many of the trailing digits as you like. E.g., '201604' is valid.")

    parser.add_argument("--collapse",
        help="An archive.org `collapse` parameter. Cf.: https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md#collapsing",
        action='append')

    parser.add_argument("--user-agent",
        help="The User-Agent header to send along with your requests to the Wayback Machine. If possible, please include the phrase 'waybackpack' and your email address. That way, if you're battering their servers, they know who to contact. Default: '{0}'.".format(DEFAULT_USER_AGENT),
        default=DEFAULT_USER_AGENT)

    parser.add_argument("--follow-redirects",
        help="Follow redirects.",
        action="store_true")

    parser.add_argument("--uniques-only",
        help="Download only the first version of duplicate files.",
        action="store_true")

    parser.add_argument("--limit",
        help="Limit number of records to return")

    parser.add_argument("--max-retries",
        help="How many times to try accessing content with 4XX or 5XX status code before skipping?",
        type=int,
        default=3)

    parser.add_argument("--quiet",
        action="store_true",
        help="Don't log progress to stderr.")

    args = parser.parse_args()
    return args


def snapshot_urls(args, session = None):
    session = session or Session(
        user_agent=args.user_agent,
        follow_redirects=args.follow_redirects,
        max_retries=args.max_retries
    )

    snapshots = search(args.url,
        session=session,
        from_date=args.from_date,
        to_date=args.to_date,
        uniques_only=args.uniques_only,
        collapse=args.collapse,
        limit=args.limit
    )

    urls = []
    for snap in snapshots:
        urls.append(
            ARCHIVE_TEMPLATE.format(
                timestamp=snap["timestamp"],
                url=args.url,
            )
        )
    return urls


if __name__ == "__main__":
    import argparse

    args = parse_args()

    logging.basicConfig(
        level=(logging.WARN if args.quiet else logging.INFO),
        format="%(levelname)s:%(name)s: %(message)s"
    )

    urls = snapshot_urls(args)
    print("\n".join(urls))

