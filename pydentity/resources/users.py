from pydentity.resources.base import PaginatedRIDListResource
from pydentity.server import APP

class UserListResource(PaginatedRIDListResource):
    def objects_iter(self, rid):
        return APP.domain_model.users_iter(rid)
