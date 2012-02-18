from pyramid.view import view_config

from .models import (
    DBSession,
    User,
    )

from . import BoxSession

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    single_user = DBSession.query(User).get(1)
    return {'single_user':single_user, 'project':'cloudyshelf'}
