from pydentity.resources.base import PaginatedPolicyHandleObjectListResource
from pydentity.server import APP

class AliasesListResource(PaginatedPolicyHandleObjectListResource):
    def objects_iter(self, rid):
        return APP.domain_model.aliases_iter(rid)
