"""Customized Application-Level Logger."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from settings.base import settings


class CustomAdapter(logging.LoggerAdapter):
    """Custom Logging Adaper. Adding Tracing UUID to logs.

    Args:
        logging (object): Basic LoggerAdapter

    """

    custom_params = (
        'event',
        'event_attrs',
    )

    def with_extra(
        self,
        level: str,
        msg: str,
        event: str,
        event_attrs: dict[str, object] | None = None,
        *args,
        **kwargs,
    ):
        """Pass extra parameters to logger record.

        Args:
            level (str): Log Level
            msg (str): Record message
            event (str): Event (basically, function or method call)
            event_attrs (dict[str, object] | None, optional): Call arguments

        Returns:
            _type_: Log Message
        """
        self.extra['event'] = event
        self.extra['event_attrs'] = event_attrs

        return super().log(logging.getLevelName(level), msg, *args, **kwargs)

    def log(
        self,
        level: str,
        msg: str,
        *args,
        **kwargs: object,
    ) -> None:
        """Create Log Record.

        Args:
            level (str): Log Level
            msg (str): Log Message

        Returns:
            None: object
        """
        self._unset_custom_params(kwargs)
        return super().log(
            level,
            msg,
            *args,
            **kwargs,
        )

    def _unset_custom_params(self, kwargs):
        for param_name in self.custom_params:
            if param_name not in kwargs:
                self.extra[param_name] = None


class CustomFormatter(logging.Formatter):
    """Custom Log Formatter. Appliable for ELK.

    Args:
        logging (object): Basic Formatting Class
    """

    def format(self, record: logging.LogRecord) -> str:
        """Return log record with tracing UUID and extra data.

        Args:
            record (logging.LogRecord): Log Record

        Returns:
            str: JSON Object with enriched Log Record
        """
        log_record = {
            'Module': record.module,
            'Message': record.msg % record.args if record.args else record.msg,
            'Level': record.levelname,
            'Source': record.name,
            'Process': record.process,
            'Thread': record.thread,
            'Event': json.dumps(
                getattr(record, 'event', None),
                default=str,
            ),
            'EventAttributes': json.dumps(
                getattr(
                    record,
                    'event_attrs',
                    None,
                ),
                default=str,
            ),
            'Date': datetime.utcfromtimestamp(record.created).strftime(
                '%Y-%m-%d %H:%M:%S,%s',
            ),
        }
        try:
            getattr(record, 'uuid', None)
        except AttributeError:
            log_record['Context_UUID'] = None
        else:
            log_record['Context_UUID'] = record.uuid

        return json.dumps(log_record)


def get_logger() -> CustomAdapter:
    """Return current configured logger.

    Returns:
        CustomAdapter: Custom Logging Adapter class
    """
    uuid = uuid4()
    logger = logging.getLogger('BeatRss')
    if logger.handlers:
        return CustomAdapter(
            logger,
            {'uuid': str(uuid)},
        )

    logger.setLevel(settings.log_level)

    formatter = CustomFormatter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(settings.log_level)

    logger.addHandler(console_handler)
    return CustomAdapter(logger, {'uuid': str(uuid)})
