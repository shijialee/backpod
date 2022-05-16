#!/usr/bin/env python

from .session import Session
from .settings import DEFAULT_USER_AGENT
from .snapshot_urls import snapshot_urls
import argparse
import logging
import datetime
from parsel import Selector
import lxml.etree as etree
from dateutil.parser import parse
import os
import uuid


logger = logging.getLogger(__name__)
static_root = os.environ.get('STATIC_ROOT', '/app/static')


def parse_args():
    parser = argparse.ArgumentParser()

    # parser.add_argument("url",
    #     help="The URL of the resource you want to download.")

    parser.add_argument("--user-agent",
        help="The User-Agent header to send along with your requests to the "
            "Wayback Machine. If possible, please include the phrase 'waybackpack' "
            "and your email address. That way, if you're battering their servers,"
            "they know who to contact. Default: '{0}'.".format(DEFAULT_USER_AGENT),
        default=DEFAULT_USER_AGENT)

    parser.add_argument("--max-retries",
        help="How many times to try accessing content with 4XX or 5XX status code before skipping?",
        type=int,
        default=3)

    parser.add_argument("--follow-redirects",
        help="Follow redirects.",
        action="store_true",
        default=True)

    parser.add_argument("--quiet",
        action="store_true",
        help="Don't log progress to stderr.")

    tmp_args = parser.parse_args()
    return tmp_args


def main(args, session, fh):
    first_request = True

    while True:
        logger.info('fetching {0}'.format(args.url))
        res = session.get(args.url)

        if res.status_code != 200:
            log_msg = 'exception: "{0}"'
            logger.info(log_msg.format(
                res.content.decode("utf-8").strip()
            ))
            break
        if 'text/xml' not in res.headers['content-type']:
            break

        parser = etree.XMLParser(strip_cdata=False)
        root = etree.fromstring(res.content, parser=parser, base_url=res.url)
        selector = Selector(root=root, type='xml')
        if selector.xpath('//item').get() is None:
            # no episode
            break

        # get episode
        episode_count = len(selector.xpath('//item'))
        first_pub_date = selector.xpath('//item')[-1].xpath('.//pubDate/text()').get()
        last_pub_date = selector.xpath('//item')[0].xpath('.//pubDate/text()').get()

        log_msg = 'show count "{0}", first pub date "{1}, last "{2}"'
        logger.info(log_msg.format(episode_count, first_pub_date, last_pub_date))

        if first_request:
            # get anything before <item> - this is the podcast detail
            index = res.text.find('<item>')
            fh.write(res.text[0:index])
            first_request = False

        # need this line, otherwise namespaces are added to each <item>
        selector.remove_namespaces()
        items = selector.xpath('//item').getall()
        fh.write("\n".join(items))

        # get wayback url
        dt = get_date(first_pub_date)
        if dt is None:
            break

        previous_date_dt = dt.date() - datetime.timedelta(days=1)
        one_year_before_dt = dt.date() - datetime.timedelta(days=365)
        args.from_date = one_year_before_dt.strftime('%Y%m%d')
        args.to_date = previous_date_dt.strftime('%Y%m%d')
        args.limit = '-2'
        args.uniques_only = True
        # reset url to the original url so we get the wayback snapshot url
        #   within the time range.
        args.url = args.original_url
        args.collapse = ['timestamp:8', 'digest']
        logger.info('search wayback from {0} to {1}'.format(args.from_date, args.to_date))
        urls = snapshot_urls(args, session)

        if urls:
            # we get wayback url and will extract feed later
            args.url = urls[0]
        else:
            break

    # if it is still first request(no episodes or fetch failed), that means we got nothing
    if first_request:
        return False
    else:
        return True


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
    except Exception as inst:
        # print(f'error parsing {datetime_str}')
        # a value of 4000000000 will overflow, so we catch all here.
        # XXX override wrong format
        logger.error(inst)
        logger.info('date format is wrong for {0}'.format(datetime_str))
        return None


def process(args):
    fetch_status = False
    args.original_url = args.url

    session = Session(
        user_agent=args.user_agent,
        max_retries=args.max_retries,
        follow_redirects=args.follow_redirects,
    )

    logging.basicConfig(
        level=(logging.WARN if args.quiet else logging.INFO),
        datefmt='%Y-%m-%d %H:%M:%S',
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s"
    )

    xml_filename = str(uuid.uuid4())
    xml_file_path = os.path.join(static_root, xml_filename)
    with open(xml_file_path, "w") as fh:
        try:
            success = main(args, session, fh)
            if success:
                fh.write("\n    </channel>\n</rss>")
                fetch_status = success
        except Exception as inst:
            logger.error(inst)

    return fetch_status, xml_filename, xml_file_path


def web_process(url):
    class Args:
        pass

    web_args = Args()
    web_args.url = url
    web_args.quiet = False
    web_args.max_retries = 3
    web_args.follow_redirects = True
    web_args.user_agent = DEFAULT_USER_AGENT
    return process(web_args)


if __name__ == "__main__":
    cli_args = parse_args()
    cli_args.url = 'https://www.npr.org/rss/podcast.php?id=510289'

    status, filename, _ = process(cli_args)
    if status:
        logger.info(f'feed is saved as {filename}')
    else:
        logger.info(f'fetch feed failed')
