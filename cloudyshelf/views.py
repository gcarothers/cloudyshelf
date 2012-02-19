from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import (
	authenticated_userid,
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
	session = request.session
	if 'user_id' in session:
		return HTTPFound(request.route_url('shelf'))
	return {}

@view_config(route_name='signup', request_method='POST')
def post_signup(request):
	session = request.session
	session['email'] = request.params['email']
	session['password'] = request.params['password']
	request_token = request.dropbox_session.obtain_request_token()
	session['request_token'] = request_token.to_string()
	authorize_url = request.dropbox_session.build_authorize_url(
		request_token, oauth_callback=request.route_url('callback', qualified=True))
	return HTTPFound(authorize_url)

@view_config(route_name='callback', request_method='GET')
def callback(request):
	session = request.session
	request_token = oauth.OAuthToken.from_string(session['request_token'])
	access_token = request.dropbox_session.obtain_access_token(request_token)
	user = User()
	user.user_name = session['email']
	user.email = session['email']
	user.set_password(session['password'])
	user.dropbox_token = access_token.to_string()
	user.status = 0
	DBSession.add(user)
	DBSession.flush()
	del session['email']
	del session['password']
	del session['request_token']
	session['user_id'] = user.id
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

@view_config(route_name='shelf', renderer='shelf.mako', permission='dropbox')
def shelf(request):
	user = request.user
	access_token = oauth.OAuthToken.from_string(user.dropbox_token)
	request.dropbox_session.set_token(access_token.key, access_token.secret)
	client = DropboxClient(request.dropbox_session)
	metadata = client.metadata('/')
	return {'user': user, 'files': metadata['contents']}

@view_config(route_name='shelf_download', permission='dropbox')
def shelf_download(request):
	user = request.user
	access_token = oauth.OAuthToken.from_string(user.dropbox_token)
	request.dropbox_session.set_token(access_token.key, access_token.secret)
	client = DropboxClient(request.dropbox_session)
	media = client.media('/' + request.matchdict['book'])
	return HTTPFound(media['url'])
