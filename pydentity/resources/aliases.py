from pydentity.resources.base import PaginatedRIDListResource
from pydentity.server import APP

class AliasesListResource(PaginatedRIDListResource):
    def objects_iter(self, rid):
        return APP.domain_model.aliases_iter(rid)
