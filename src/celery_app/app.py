"""Basic Celery config for application."""

from celery import Celery
from settings.base import settings

app = Celery('tasks', broker=settings.celery.broker_url)
