__all__ = ['DropboxFile']

from .base import *

from sqlalchemy import (
	Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
    )

class DropboxFile(Base):
	"""Tracks files under the application directory. Book files will be linked
	to a book and moved into a proper folder hierarchy; non-book files will be
	left in place and marked as such."""

	__tablename__ = 'dropbox_file'

	path = Column(Text, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	revision = Column(Text, nullable=False)
	non_book = Column(Boolean, nullable=False, default=bool)
	book_id = Column(Integer, nullable=True)
