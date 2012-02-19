from pyramid.security import (
    Allow,
    Authenticated,
    Deny,
    Everyone,
)

from .models import (
	DBSession,
	User
)

class SimpleContext(object):
    def __init__(self, request):
        pass

    __acl__ = [
        (Allow, 'group:dropbox_allowed', 'dropbox allowed'),
        (Allow, Authenticated, 'logged in'),
    ]

def session_callback(userid, request):
    user = DBSession.query(User).get(userid)
    if not user:
    	return None
    request.user = user
    principals = [userid,]
    if user.dropbox_token:
    	principals.append('group:dropbox')
    return principals
