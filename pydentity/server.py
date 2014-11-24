from flask import Flask, redirect
from flask.ext.admin import Admin, AdminIndexView, expose

class AdminHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

APP = Flask(__name__)
ADMIN = Admin(APP, name="pydentity", index_view=AdminHomeView())

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

def run(server_args):
    add_admin_views()
    APP.run(**server_args.__dict__)
