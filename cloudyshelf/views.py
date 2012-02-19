from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import (
	authenticated_userid,
	effective_principals,
	forget,
	remember,
)
from oauth import oauth
from dropbox.client import DropboxClient

from .models import (
    DBSession,
    User,
    )

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    single_user = DBSession.query(User).get(1)
    return {'single_user':single_user, 'project':'cloudyshelf'}

@view_config(route_name='signup', renderer='signup.mako', request_method='GET')
def signup(request):
	if authenticated_userid(request):
		return HTTPFound(request.route_url('shelf'))
	return {}

@view_config(route_name='signup', request_method='POST')
def post_signup(request):
	user = User()
	user.user_name = request.params['email']
	user.email = request.params['email']
	user.set_password(request.params['password'])
	user.status = 0
	DBSession.add(user)
	DBSession.flush()

	request.response.headerlist.extend(
		remember(request, user.id),
	)
	return HTTPFound(request.route_url('shelf'))

@view_config(route_name='allow_dropbox', renderer='allow_dropbox.mako', request_method='GET')
def allow_dropbox(requset):
	return {}

@view_config(route_name='allow_dropbox', request_method='POST')
def post_allow_dropbox(request):
	request_token = request.dropbox_session.obtain_request_token()
	request.session['request_token'] = request_token.to_string()
	authorize_url = request.dropbox_session.build_authorize_url(
		request_token, oauth_callback=request.route_url('oauth_callback', qualified=True))
	return HTTPFound(authorize_url)

@view_config(route_name='oauth_callback', request_method='GET', permission='logged in')
def oauth_callback(request):
	user = request.user
	request_token = oauth.OAuthToken.from_string(request.session['request_token'])
	del request.session['request_token']
	assert request_token.key == request.params['oauth_token']
	access_token = request.dropbox_session.obtain_access_token(request_token)
	user.dropbox_token = access_token.to_string()
	return HTTPFound(request.route_url('shelf'))

@view_config(route_name='login', renderer='login.mako', request_method='GET')
def login(request):
	if authenticated_userid(request):
		return HTTPFound(request.route_url('shelf'))
	return {}

@view_config(route_name='login', request_method='POST')
def post_login(request):
	user = User.by_user_name(user_name=request.params['email'])
	if not user.check_password(request.params['password']):
		return HTTPFound(request.route_url('login'))
	request.response.headerlist.extend(
		remember(request, user.id),
	)
	return HTTPFound(request.route_url('shelf'))

@view_config(route_name='logout', permission='logged in')
def logout(request):
	request.response.headerlist.extend(
		forget(request),
	)
	return HTTPFound(request.route_url('login'))

@view_config(route_name='shelf', renderer='shelf.mako', permission='dropbox allowed')
def shelf(request):
	user = request.user
	access_token = oauth.OAuthToken.from_string(user.dropbox_token)
	request.dropbox_session.set_token(access_token.key, access_token.secret)
	client = DropboxClient(request.dropbox_session)
	metadata = client.metadata('/')
	return {'user': user, 'files': metadata['contents']}

@view_config(route_name='shelf_download', permission='dropbox allowed')
def shelf_download(request):
	user = request.user
	access_token = oauth.OAuthToken.from_string(user.dropbox_token)
	request.dropbox_session.set_token(access_token.key, access_token.secret)
	client = DropboxClient(request.dropbox_session)
	media = client.media('/' + request.matchdict['book'])
	return HTTPFound(media['url'])

def forbidden_view(request):
	if not authenticated_userid(request):
		return HTTPFound(request.route_url('login'))
	if authenticated_userid(request) and not 'group:dropbox_allowed' in effective_principals(request):
		return HTTPFound(request.route_url('allow_dropbox'))
