"""Celery Tasks frontend module."""

from http import HTTPStatus
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from celery_app.app import app
from db.engine import get_session
from db.models import HTMLLink, RSSLink
from log.app_logger import get_logger
from settings.base import settings
from shared.parsing.pages import parse_electrobeats_page


def _store_links_in_db(
    html_links: list[HttpUrl],
    rss_link: HttpUrl,
    rss_title: str,
) -> None:
    for link in html_links:
        with get_session() as session:
            html_link = HTMLLink(
                rss_link=rss_link,
                rss_title=rss_title,
                html_link=link,
            )
            session.add(html_link)
            session.commit()


@app.task
def parse_html_and_store(rss_link: HttpUrl, rss_title: str) -> None:
    """Parse HTML page and save found links in db.

    Args:
        rss_link (HttpUrl): RSS Link
        rss_title (str): RSS Title

    Returns:
        None
    """
    # Store HTML links in the database
    dl_links = parse_electrobeats_page(rss_link)
    if not dl_links:
        return

    soup = BeautifulSoup(dl_links, 'html.parser')
    html_links = [found['href'] for found in soup.find_all('a')]
    _store_links_in_db(html_links, rss_link=rss_link, rss_title=rss_title)

    # Publish HTML links to Telegram
    links_message = '\n'.join(
        [
            '[{0}]({1})'.format(
                urlparse(link).netloc,
                link,
            )
            for link in html_links
        ],
    )
    message = f'*Title*: {rss_title}\n\n*Download*\n\n: {links_message}'
    send_telegram_task.delay(message=message)

    get_logger().info(
        'HTML links stored and published to Telegram successfully',
    )


def _find_existing_entry(rss_link: str):
    with get_session() as session:
        return session.query(
            RSSLink,
        ).filter_by(
            rss_link=rss_link,
        ).first()


def _add_entry(rss_link: HttpUrl, rss_title: str):
    with get_session() as session:
        rss_link_obj = RSSLink(rss_link=rss_link, rss_title=rss_title)
        session.add(rss_link_obj)
        session.commit()


@app.task
def fetch_rss_feed():
    """Fetch RSS feed and pass to parser."""
    feed = feedparser.parse(settings.rss.elektrobeats.url)

    for entry in feed.entries:
        rss_link = entry.link
        rss_title = entry.title or entry.description

        # Check if the item already exists in the database
        if _find_existing_entry(rss_link=rss_link):
            continue

        _add_entry(rss_link=rss_link, rss_title=rss_title)

        # Call the coroutine to parse the HTML and obtain HTML links
        parse_html_and_store.delay(rss_link, rss_title)

        get_logger().info(
            'RSS feed fetched and new items stored in the database',
        )


@app.task
def send_telegram_task(message: str):
    """Send message to Telegram.

    Args:
        message (str): Message Body

    Returns:
        Callable: Send to Telegram Function
    """
    return send_telegram(message)


def send_telegram(message) -> bool:
    """Send message to Telegram channel.

    Args:
        message (str): Message

    Returns:
        bool: Is OK?
    """
    url = (
        'https://api.telegram.org/bot'
        + settings.telegram.token
        + '/sendMessage'
    )
    request_params = {
        'chat_id': settings.telegram.chat_id,
        'text': message,
        'parse_mode': 'markdown',
        'disable_web_page_preview': True,
    }
    response = requests.post(
        url,
        params=request_params,
        timeout=settings.http.default_timeout,
    )
    get_logger().error(
        {
            'code': response.status_code,
            'message': message,
            'data': response.json(),
        },
    )
    return response.status_code in {HTTPStatus.OK, HTTPStatus.ACCEPTED}
