from pydentity.resources.base import PaginatedPolicyHandleObjectListResource
from pydentity.server import APP

class GroupsListResource(PaginatedPolicyHandleObjectListResource):
    def objects_iter(self, rid):
        return APP.domain_model.groups_iter(rid)
