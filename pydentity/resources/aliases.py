from pydentity.models.samba_ import Alias
from pydentity.resources.base import (
    PaginatedPolicyHandleObjectListResource,
    PolicyHandleObjectResource,
)
from pydentity.server import APP

class AliasListResource(PaginatedPolicyHandleObjectListResource):
    def objects_iter(self, rid):
        return APP.domain_model.aliases_iter(rid)

class AliasResource(PolicyHandleObjectResource):
    def get_object(self, object_rid):
        return Alias(APP.domain_model, object_rid)
