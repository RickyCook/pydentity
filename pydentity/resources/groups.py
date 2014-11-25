from pydentity.resources.base import PaginatedRIDListResource
from pydentity.server import APP

class GroupsListResource(PaginatedRIDListResource):
    def objects_iter(self, rid):
        return APP.domain_model.groups_iter(rid)
