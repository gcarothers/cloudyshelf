from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from dropbox import client, rest, session

from .models import DBSession

BoxSession = None

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    BoxSession = setup_dropbox_session(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()

def setup_dropbox_session(settings):
	app_key = settings['dropbox.app_key']
	app_secret = settings['dropbox.app_secret']
	access_type = 'app_folder'
	return session.DropboxSession(app_key, app_secret, access_type)