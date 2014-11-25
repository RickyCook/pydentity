from flask import Flask, redirect
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.restful import Api

class AdminHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

APP = Flask(__name__)
ADMIN = Admin(APP, name="pydentity", index_view=AdminHomeView())
API1 = Api(APP, prefix='/api/v1')

@APP.route('/')
def index():
    """
    Index instantly redirects to the admin panel
    """
    return redirect(ADMIN.url)

def add_admin_views():
    from pydentity import views
    ADMIN.add_view(views.admin_samba.AdminUsersView(name="Users",
                                                    endpoint="users"))

def add_api_resources():
    from pydentity import resources
    API1.add_resource(resources.users.UserListResource, '/users')

def setup_samba(app_args):
    from pydentity.samba_util import SAMRHandle
    from pydentity.models.samba_ import Domain

    APP.samr_handle = SAMRHandle(conf_file=app_args.smbconf)
    APP.domain_model = Domain(app_args.smbdomain, APP.samr_handle)

def run(app_args):
    setup_samba(app_args)
    add_admin_views()
    add_api_resources()

    server_args = {
        key: val
        for key, val in app_args.__dict__.items()
        if key in ('host', 'port', 'debug')
    }
    APP.run(**server_args)
