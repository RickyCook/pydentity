from flask.ext.admin import AdminIndexView, expose

from pydentity.views import admin_samba

class AdminHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return "boop"
