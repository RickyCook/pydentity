from pydentity.models.samba_ import Group
from pydentity.resources.base import (
    PaginatedPolicyHandleObjectListResource,
    PolicyHandleObjectResource,
)
from pydentity.server import APP

class GroupListResource(PaginatedPolicyHandleObjectListResource):
    def objects_iter(self, rid):
        return APP.domain_model.groups_iter(rid)

class GroupResource(PolicyHandleObjectResource):
    def get_object(self, object_rid):
        return Group(APP.domain_model, object_rid)
