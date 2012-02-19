from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
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

@view_config(route_name='signup', renderer='templates/signup.pt', request_method='GET')
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

@view_config(route_name='login', renderer='templates/login.pt', request_method='GET')
def login(request):
	session = request.session
	session['user_id'] = 1
	if 'user_id' in session:
		return HTTPFound(request.route_url('shelf'))
	return {}

@view_config(route_name='login', request_method='POST')
def post_login(request):
	pass

@view_config(route_name='shelf', renderer='shelf.mako')
def shelf(request):
	session = request.session
	user = DBSession.query(User).get(session['user_id'])
	access_token = oauth.OAuthToken.from_string(user.dropbox_token)
	request.dropbox_session.set_token(access_token.key, access_token.secret)
	client = DropboxClient(request.dropbox_session)
	metadata = client.metadata('/')
	return {'user': user, 'files': metadata['contents']}

@view_config(route_name='shelf_download')
def shelf_download(request):
	session = request.session
	user = DBSession.query(User).get(session['user_id'])
	access_token = oauth.OAuthToken.from_string(user.dropbox_token)
	request.dropbox_session.set_token(access_token.key, access_token.secret)
	client = DropboxClient(request.dropbox_session)
	media = client.media('/' + request.matchdict['book'])
	return HTTPFound(media['url'])
