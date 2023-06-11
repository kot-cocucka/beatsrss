
from datetime import datetime

import requests
from pydantic import HttpUrl

from log.app_logger import get_logger
from settings.base import settings


def parse_electrobeats_page(page_link: HttpUrl) -> list[str | None]:
    """Parse page link for electrobeats.org and return download links.

    Args:
        page_link (HttpUrl): Electrobeats.org page link

    Returns:
        _type_: _description_
    """
    try:
        page_id = page_link.split('https://elektrobeats.org/')[-1]
    except Exception as exc:
        get_logger().exception(exc)
        return []

    timestamp_ms = int(datetime.now().timestamp() * 1000)

    url = (
        'https://elektrobeats.org/music.php'
        + '?task=getdownloadlink&id='
        + str(page_id)
        + '&_='
        + str(timestamp_ms)
    )
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': (
            'https://elektrobeats.org/'
            + str(page_id)
        ),
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=settings.http.default_timeout,
    )
    return response.text
