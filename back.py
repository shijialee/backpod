#!/usr/bin/env python
from .session import Session
from .settings import DEFAULT_USER_AGENT, DEFAULT_ROOT
from .snapshot_urls import snapshot_urls
import argparse
import logging
import datetime
from parsel import Selector
from dateutil.parser import parse


logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("url",
        help="The URL of the resource you want to download.")

    parser.add_argument("--user-agent",
        help="The User-Agent header to send along with your requests to the Wayback Machine. If possible, please include the phrase 'waybackpack' and your email address. That way, if you're battering their servers, they know who to contact. Default: '{0}'.".format(DEFAULT_USER_AGENT),
        default=DEFAULT_USER_AGENT)

    parser.add_argument("--max-retries",
        help="How many times to try accessing content with 4XX or 5XX status code before skipping?",
        type=int,
        default=3)

    parser.add_argument("--quiet",
        action="store_true",
        help="Don't log progress to stderr.")

    args = parser.parse_args()
    return args


def main(args, session):
    urls = snapshot_urls(args, session)

def main(args, session):
    res = session.get(args.url)

    if res.status_code != 200:
        log_msg = 'exception: "{0}"'
        logger.info(log_msg.format(
            res.content.decode("utf-8").strip()
        ))
        return None

    selector = Selector(text=res.text)
    selector.register_namespace('itunes','http://www.itunes.com/dtds/podcast-1.0.dtd')
    if selector.xpath('//item').get() is None:
        # no shows
        return None
    else:
        # get shows
        episode_count = len(selector.xpath('//item'))
        first_pub_date = selector.xpath('//item')[-1].xpath('.//pubdate/text()').get()
        last_pub_date = selector.xpath('//item')[0].xpath('.//pubdate/text()').get()

        log_msg = 'show count "{0}", earliest pub date "{1}"'
        logger.info(log_msg.format(episode_count, first_pub_date))

        items = selector.xpath('//item').getall()
        print("\n".join(items))


def get_date(datetime_str):
    """
    change from 'Wed, 29 Mar 2017 00:00:00 GMT' to '29 Mar 2017'
    replace invalid datetime str to None to avoid showing bad result
    """
    if datetime_str is None:
        return datetime_str
    if not isinstance(datetime_str, str):
        return None

    try:
        dt = parse(datetime_str)
        return dt
    except:
        # print(f'error parsing {datetime_str}')
        # a value of 4000000000 will overflow, so we catch all here.
        # XXX override wrong format
        logger.info('date format is wrong for {0}'.format(datetime_str))
        return None


if __name__ == "__main__":
    args = parse_args()

    logging.basicConfig(
        level=(logging.WARN if args.quiet else logging.INFO),
        format="%(levelname)s:%(name)s: %(message)s"
    )

    session = Session(
        user_agent=args.user_agent,
        max_retries=args.max_retries
    )

    main(args, session)
