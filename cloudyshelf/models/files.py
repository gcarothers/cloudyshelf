__all__ = ['ScannedFile']

from .base import *

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    )

class ScannedFile(Base):
	"""Records a file that we've scanned and copied to the 'unprocessed'
	directory. Only records files outside of the 'special' 'unprocessed' and
	'sorted' directories."""

	__tablename__ = 'scanned_file'

	filename = Column(Text, primary_key=True)
	revision = Column(Text, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
