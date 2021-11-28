#!/usr/bin/env python
from .session import Session
from .settings import DEFAULT_USER_AGENT, DEFAULT_ROOT
from .snapshot_urls import snapshot_urls
import argparse
import logging
import datetime
from parsel import Selector
import lxml.etree as etree
from dateutil.parser import parse


logger = logging.getLogger(__name__)
main_url = None
close_tag = False


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

    parser.add_argument("--follow-redirects",
        help="Follow redirects.",
        action="store_true")

    parser.add_argument("--quiet",
        action="store_true",
        help="Don't log progress to stderr.")

    args = parser.parse_args()
    return args


def main(args, session, first_request=False):
    logger.info('fetching {0}'.format(args.url))
    res = session.get(args.url)

    if res.status_code != 200:
        log_msg = 'exception: "{0}"'
        logger.info(log_msg.format(
            res.content.decode("utf-8").strip()
        ))
        return None
    if 'text/xml' not in res.headers['content-type']:
        return None

    parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(res.content, parser=parser, base_url=res.url)
    selector = Selector(root=root, type='xml')
    if selector.xpath('//item').get() is None:
        # no shows
        return None
    else:
        # get shows
        episode_count = len(selector.xpath('//item'))
        first_pub_date = selector.xpath('//item')[-1].xpath('.//pubDate/text()').get()
        last_pub_date = selector.xpath('//item')[0].xpath('.//pubDate/text()').get()

        log_msg = 'show count "{0}", first pub date "{1}, last "{2}"'
        logger.info(log_msg.format(episode_count, first_pub_date, last_pub_date))

        if first_request:
            # open tag
            index = res.text.find('<item>')
            print(res.text[0:index])
            close_tag = True

        # need this line, otherwise namespaces are added to each <item>
        selector.remove_namespaces()
        items = selector.xpath('//item').getall()
        print("\n".join(items))

        # get wayback url
        dt = get_date(first_pub_date)
        if dt is None:
            return

        previous_date_dt = dt.date() - datetime.timedelta(days=1)
        one_year_before_dt = dt.date() - datetime.timedelta(days=365)
        args.from_date = one_year_before_dt.strftime('%Y%m%d')
        args.to_date = previous_date_dt.strftime('%Y%m%d')
        args.limit = '-2'
        args.uniques_only = True
        # reset to get the snapshot url for the original url
        args.url = main_url
        args.collapse = ['timestamp:8', 'digest']
        logger.info('from {0} to {1}'.format(args.from_date, args.to_date))
        urls = snapshot_urls(args, session)

        if urls:
            # we get wayback url here
            args.url = urls[0]
            main(args, session)


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
    main_url = args.url
    first_request = True

    logging.basicConfig(
        level=(logging.WARN if args.quiet else logging.INFO),
        format="%(levelname)s:%(name)s: %(message)s"
    )

    session = Session(
        user_agent=args.user_agent,
        max_retries=args.max_retries,
        follow_redirects=args.follow_redirects,
    )

    main(args, session, first_request)
    if close_tag:
        print("\n    </channel>\n</rss>")

