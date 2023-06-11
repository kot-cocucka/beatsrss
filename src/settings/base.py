"""Settings module."""

from pydantic import BaseSettings, Field


class _TelegramSettings(BaseSettings):
    token: str = Field(..., env='TELEGRAM_TOKEN')
    chat_id: str | None = Field(None, env='TELEGRAM_CHAT_ID')


class _ElektrobeatsRssSettings(BaseSettings):
    url = 'https://elektrobeats.org/music?task=rss'


class _RssSettings(BaseSettings):
    elektrobeats = _ElektrobeatsRssSettings()
    default_fetch_timeout = 600


class _DbSettings(BaseSettings):
    host: str = Field(..., env='POSTGRES_HOST')
    name: str = Field(..., env='POSTGRES_DB')
    user: str = Field(..., env='POSTGRES_USER')
    password: str = Field(..., env='POSTGRES_PASSWORD')

    @property
    def as_dsn(self):
        return (
            f'dbname={self.name} '
            + f'user={self.user} '
            + f'password={self.password} '
            + f'host={self.host}'
        )

    @property
    def as_engine(self):
        return (
            'postgresql+psycopg://'
            + f'{self.user}:{self.password}'
            + f'@{self.host}/{self.name}'
        )


class _CelerySettings(BaseSettings):
    broker_url: str = Field(..., env='CELERY_BROKER_URL')


class _HttpSettings(BaseSettings):
    default_timeout = 10


class AppSettings(BaseSettings):
    """Main Settings module."""

    rss = _RssSettings()
    db = _DbSettings()
    celery = _CelerySettings()
    telegram = _TelegramSettings()
    http = _HttpSettings()

    log_level = 'INFO'


settings = AppSettings()
