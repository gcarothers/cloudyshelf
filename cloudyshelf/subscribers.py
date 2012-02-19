from dropbox import session
from pyramid.events import (
	ContextFound,
	subscriber,
	)

@subscriber(ContextFound)
def make_dropbox_session(event):
	settings = event.request.registry
	if 'dropbox.app_key' in settings:
		app_key = settings['dropbox.app_key']
		app_secret = settings['dropbox.app_secret']
		access_type = 'app_folder'
		event.request.dropbox_session = session.DropboxSession(app_key, app_secret, access_type)
