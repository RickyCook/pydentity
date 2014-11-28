from flask import Flask, redirect
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.restful import Api

class AdminHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', domain=APP.domain_model)

APP = Flask(__name__)
ADMIN = Admin(APP,
              name="pydentity",
              index_view=AdminHomeView(),
              base_template='admin/layout_.html')
API1 = Api(APP, prefix='/api/v1')

@APP.route('/')
def index():
    """
    Index instantly redirects to the admin panel
    """
    return redirect(ADMIN.url)

def add_admin_views(app_args):
    from pydentity.views.admin_samba import AdminObjectsListView
    ADMIN.add_view(AdminObjectsListView(name="Users", endpoint="users"))
    ADMIN.add_view(AdminObjectsListView(name="Groups", endpoint="groups"))
    ADMIN.add_view(AdminObjectsListView(name="Aliases", endpoint="aliases"))

    if app_args['debug']:
        from pydentity.views.debug_api_browse import DebugAPIBrowseView
        ADMIN.add_view(DebugAPIBrowseView(name="Browse API",
                                          endpoint="debug_api_browse"))

def add_api_resources(_):
    from pydentity import resources
    API1.add_resource(resources.aliases.AliasListResource, '/aliases')
    API1.add_resource(resources.groups.GroupListResource, '/groups')
    API1.add_resource(resources.users.UserListResource, '/users')

    API1.add_resource(resources.aliases.AliasResource, '/aliases/<int:object_rid>')
    API1.add_resource(resources.groups.GroupResource, '/groups/<int:object_rid>')
    API1.add_resource(resources.users.UserResource, '/users/<int:object_rid>')

def setup_samba(app_args):
    from pydentity.samba_util import SAMRHandle
    from pydentity.models.samba_ import Domain

    APP.samr_handle = SAMRHandle(conf_file=app_args['smbconf'])
    APP.domain_model = Domain(app_args['smbdomain'], APP.samr_handle)

def run(app_args):
    setup_samba(app_args)
    add_admin_views(app_args)
    add_api_resources(app_args)

    server_args = {
        key: val
        for key, val in app_args.items()
        if key in ('host', 'port', 'debug')
    }
    APP.run(**server_args)
