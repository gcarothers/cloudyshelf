__all__ = ['Group', 'GroupPermission', 'UserGroup', 'GroupResourcePermission',
           'Resource', 'UserPermission', 'UserResourcePermission', 'User',
           'ExternalIdentity',]

from .base import *

from sqlalchemy import (
    Column,
    Text,
    )

import ziggurat_foundations.models
from ziggurat_foundations.models import (
    BaseModel, UserMixin, GroupMixin, GroupPermissionMixin, UserGroupMixin,
    GroupResourcePermissionMixin, ResourceMixin, UserPermissionMixin,
    UserResourcePermissionMixin, ExternalIdentityMixin,
    )
from ziggurat_foundations import ziggurat_model_init
# this is needed for pylons 1.0 / akhet approach to db session
ziggurat_foundations.models.DBSession = DBSession
# optional for folks who pass request.db to model methods

# Base is sqlalchemy's Base = declarative_base() from your project
class Group(GroupMixin, Base):
    pass

class GroupPermission(GroupPermissionMixin, Base):
    pass

class UserGroup(UserGroupMixin, Base):
    pass

class GroupResourcePermission(GroupResourcePermissionMixin, Base):
    pass

class Resource(ResourceMixin, Base):
    pass

class UserPermission(UserPermissionMixin, Base):
    pass

class UserResourcePermission(UserResourcePermissionMixin, Base):
    pass

class User(UserMixin, Base):
    dropbox_token = Column(Text)

class ExternalIdentity(ExternalIdentityMixin, Base):
    pass

ziggurat_model_init(User, Group, UserGroup, GroupPermission, UserPermission,
               UserResourcePermission, GroupResourcePermission, Resource,
               ExternalIdentity, passwordmanager=None)
