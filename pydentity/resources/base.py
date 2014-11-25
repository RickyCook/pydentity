from itertools import islice

from flask.ext.restful import fields, marshal, Resource, reqparse

from pydentity.resources import fields as my_fields

RID_OBJECTS_FIELDS = {
    'name': fields.String(),
    'rid': fields.Integer(),
}

PAGINATED_RID_LIST_PARSER = reqparse.RequestParser()
PAGINATED_RID_LIST_PARSER.add_argument("rid", type=int, default=-1,
                                       help="RID to start page after")
PAGINATED_RID_LIST_PARSER.add_argument("limit", type=int, default=20,
                                       help="Limit objects returned")

class PaginatedRIDListResource(Resource):
    @property
    def objects_fields(self):
        """
        Fields structure for the objects in this list
        """
        return RID_OBJECTS_FIELDS

    @property
    def list_fields(self):
        """
        Fields structure for the list
        """
        endpoint_default = self.__class__.__name__.lower()
        return {
            'next': my_fields.UrlQS(endpoint_default, absolute=True),
            'objects': fields.List(fields.Nested(self.objects_fields)),
        }

    def objects_iter(self, rid):
        """
        Get an iterator for the objects in this resource, starting after RID
        """
        return []

    def objects(self, rid, limit):
        """
        Get the objects for this resource, starting after RID, and obeying the
        limit parameter
        """
        return islice(self.objects_iter(rid), 0, limit)

    def get(self, **kwargs):
        args = PAGINATED_RID_LIST_PARSER.parse_args()

        data = {
            'objects': list(self.objects(args['rid'], args['limit'])),
        }

        if len(data['objects']) == args['limit']:
            data['next'] = {'rid': data['objects'][-1].rid,
                            'limit': args['limit'],
                            }

        return marshal(data, self.list_fields)
