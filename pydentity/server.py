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

def run(server_args):
    add_admin_views()
    add_api_resources()
    APP.run(**server_args.__dict__)
