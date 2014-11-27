from pydentity.resources.base import PaginatedPolicyHandleObjectListResource
from pydentity.server import APP

class UsersListResource(PaginatedPolicyHandleObjectListResource):
    def objects_iter(self, rid):
        return APP.domain_model.users_iter(rid)
