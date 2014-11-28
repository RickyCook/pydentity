from itertools import islice

from flask import url_for
from flask.ext.restful import fields, marshal, Resource, reqparse

from pydentity.resources import fields as my_fields
from pydentity.util import SIMPLE_PRINTABLE_TYPES

PAGINATED_POLICY_HANDLE_OBJECT_LIST_PARSER = reqparse.RequestParser()
PAGINATED_POLICY_HANDLE_OBJECT_LIST_PARSER.add_argument(
    "rid", type=int, default=None, help="RID to start page after")
PAGINATED_POLICY_HANDLE_OBJECT_LIST_PARSER.add_argument(
    "limit", type=int, default=20, help="Limit objects returned")

class PaginatedPolicyHandleObjectListResource(Resource):
    @property
    def detail_endpoint(self):
        """
        The endpoint for the detail resource of this type
        """
        if not self.endpoint.endswith('listresource'):
            raise NotImplementedException(
                "Detail resource name can not be inferred. Must override "
                "detail_endpoint"
            )

        return "%sresource" % self.endpoint[:-12]

    @property
    def objects_fields(self):
        """
        Fields structure for the objects in this list
        """
        return {
            'rid': fields.Integer,
            'name': fields.String,
            'detail': fields.String,
        }

    @property
    def list_fields(self):
        """
        Fields structure for the list
        """
        return {
            'next': my_fields.UrlQS(self.endpoint),
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
        args = PAGINATED_POLICY_HANDLE_OBJECT_LIST_PARSER.parse_args()

        data = {'objects': [
            {
                'rid': obj.rid,
                'name': obj.name,
                'detail': url_for(self.detail_endpoint, object_rid=obj.rid),
            }
            for obj in self.objects(args['rid'], args['limit'])
        ]}

        if len(data['objects']) == args['limit']:
            data['next'] = {'rid': data['objects'][-1].rid,
                            'limit': args['limit'],
                            }

        import logging;
        logging.info(self.list_fields)
        logging.info(self.list_fields['objects'].__dict__)
        logging.info(self.list_fields['objects'].container.__dict__)
        logging.info(data)
        return marshal(data, self.list_fields)


class PolicyHandleObjectResource(Resource):
    def get_object(self, object_id):
        raise NotImplementedException("Must override get_object")

    @property
    def blacklisted_fields(self):
        """
        Fields to be removed from the result object attrs
        """
        return ()

    @property
    def fields(self):
        """
        Flask-RESTful fields to marshal the object with
        """
        return {}

    def get(self, object_rid):
        obj = self.get_object(object_rid)
        data = obj.attrs

        # Force standard name
        data['name'] = obj.name
        data['rid'] = object_rid

        # Remove blacklisted fields
        for attr_name in self.blacklisted_fields:
            data.pop(attr_name, None)

        # Generate fields
        obj_fields = self.fields
        raw_field_attrs = set(data.keys()) - set(obj_fields.keys())
        for attr_name in raw_field_attrs:
            if isinstance(data[attr_name], SIMPLE_PRINTABLE_TYPES):
                obj_fields[attr_name] = fields.Raw

        return marshal(data, obj_fields)
