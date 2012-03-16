__all__ = ['DBSession', 'Base',]

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
