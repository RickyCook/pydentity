from pydentity.models.samba_ import User
from pydentity.resources.base import (
    PaginatedPolicyHandleObjectListResource,
    PolicyHandleObjectResource,
)
from pydentity.server import APP

class UserListResource(PaginatedPolicyHandleObjectListResource):
    def objects_iter(self, rid):
        return APP.domain_model.users_iter(rid)

class UserResource(PolicyHandleObjectResource):
    def get_object(self, object_rid):
        return User(APP.domain_model, object_rid)
