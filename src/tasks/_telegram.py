from http import HTTPStatus

import requests

from celery_app.app import app
from log.app_logger import get_logger
from settings.base import settings


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
