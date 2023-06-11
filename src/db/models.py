from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from db.engine import Base


class _TimestampedDbModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class RSSLink(_TimestampedDbModel):
    __tablename__ = 'rss_links'

    rss_link = Column(String)
    rss_title = Column(String)


class HTMLLink(_TimestampedDbModel):
    __tablename__ = 'html_links'

    rss_link = Column(String)
    rss_title = Column(String)
    html_link = Column(String)
