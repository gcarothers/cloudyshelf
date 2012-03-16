import os.path

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
    ScannedFile,
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
	metadata = request.client.metadata('/')
	return {'user': user, 'files': metadata['contents']}

@view_config(route_name='shelf_download', permission='dropbox allowed')
def shelf_download(request):
	user = request.user
	media = request.client.media('/' + request.matchdict['book'])
	return HTTPFound(media['url'])

def forbidden_view(request):
	if not authenticated_userid(request):
		return HTTPFound(request.route_url('login'))
	if authenticated_userid(request) and not 'group:dropbox' in effective_principals(request):
		return HTTPFound(request.route_url('allow_dropbox'))

@view_config(route_name='scan_for_new_books', permission='dropbox allowed')
def scan_for_new_books(request):
	user = request.user
	# Presuming that dropbox directory structure does not loop back on itself...
	directory_queue = ['/']
	skip = ('/unsorted',)
	while directory_queue:
		current_folder = directory_queue.pop()
		metadata = request.client.metadata(current_folder)
		for f in metadata['contents']:
			if f['path'] in skip:
				continue
			if f['is_dir']:
				directory_queue.append(f['path'])
				continue
			if f['path'] in user.scanned_files:
				scanned_file = user.scanned_files[f['path']]
			if f['path'] not in user.scanned_files or scanned_file.revision != f['rev']:
				request.client.file_copy(
					f['path'], os.path.join('/unsorted', f['path'][1:]))
				if f['path'] in user.scanned_files:
					scanned_file.revision = f['rev']
				else:
					scanned_file = ScannedFile()
					scanned_file.path = f['path']
					scanned_file.rev = f['rev']
					user.scanned_files.set(scanned_file)
