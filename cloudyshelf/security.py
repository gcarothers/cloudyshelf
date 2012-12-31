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

from oauth2 import oauth
from dropbox.client import DropboxClient

class SimpleContext(object):
    def __init__(self, request):
        pass

    __acl__ = [
        (Allow, 'group:dropbox', 'dropbox allowed'),
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
        access_token = oauth.OAuthToken.from_string(user.dropbox_token)
        request.dropbox_session.set_token(access_token.key, access_token.secret)
        request.client = DropboxClient(request.dropbox_session)
    return principals