from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from .models import DBSession, Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    session_factory = UnencryptedCookieSessionFactoryConfig(settings['pyramid.session_secret'])
    authentication_policy = SessionAuthenticationPolicy()
    authorzaton_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, session_factory=session_factory)
    # config.set_authentication_policy(authentication_policy)
    # config.set_authorization_policy(authorzaton_policy)

    config.registry['dropbox.app_key'] = settings['dropbox.app_key']
    config.registry['dropbox.app_secret'] = settings['dropbox.app_secret']

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('signup', '/signup')
    config.add_route('callback', '/callback')
    config.add_route('shelf', '/shelf')
    config.add_route('shelf_download', '/shelf/{book}/download')
    config.scan()
    config.scan('cloudyshelf.subscribers')

    return config.make_wsgi_app()

def setup_dropbox_session(settings):
	return 
