from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import oauth

from .models import (
    DBSession,
    User,
    )

from . import BoxSession

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    single_user = DBSession.query(User).get(1)
    return {'single_user':single_user, 'project':'cloudyshelf'}

@view_config(route_name='signup', renderer='templates/signup.pt', request_method='GET')
def signup(request):
	return {}

@view_config(route_name='signup', request_method='POST')
def post_signup(request):
	session = request.session
	session['email'] = request.params['email']
	session['password'] = request.params['password']
	request_token = BoxSession.obtain_request_token()
	session['request_token'] = request_token.to_string()
	authorize_url = BoxSession.build_authorize_url(
		request_token, oauth_callback=request.url('callback', qualified=True))
	return HTTPFound(authorize_url)

@view_config(route_name='callback', request_method='GET')
def callback(request):
	session = request.session
	request_token = oauth.OAuthToken.from_string(session['request_token'])
	access_token = BoxSession.obtain_access_token(request_token)
	user = User()
	user.user_name = session['email']
	user.set_password(session['password'])
	user.dropbox_token = access_token.to_string()
	DBSession.add(user)
	DBSession.flush()
	del session['email']
	del session['password']
	del session['request_token']
	session['user_id'] = user.id
	return HTTPFound(request.url('shelf'))

@view_config(route_name='login', renderer='templates/login.pt', request_method='GET')
def login(request):
	pass

@view_config(route_name='login', request_method='POST')
def post_login(request):
	pass

@view_config(route_name='shelf', renderer='templates/shelf.pt')
def shelf(request):
	pass
