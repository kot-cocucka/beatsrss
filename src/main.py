"""Main module."""

import asyncio

from db.engine import create_all_hook
from log.app_logger import get_logger
from settings.base import settings
from tasks.tasks import fetch_rss_feed


async def main():
    """Application main function.

    Creates DB and launch RSS Feed Fetch.
    """
    create_all_hook()

    # Fetch the RSS feed periodically
    get_logger().info('Pooling RSS...')
    while True:
        try:
            fetch_rss_feed.delay()
        except Exception as exc:
            get_logger().error(
                (
                    'An error occurred while fetching the RSS feed: '
                    + str(exc)
                ),
            )

        await asyncio.sleep(settings.rss.default_fetch_timeout)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        get_logger().info('Program interrupted by user')
    finally:
        loop.close()
