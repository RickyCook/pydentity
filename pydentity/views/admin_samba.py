
from flask.ext.admin import BaseView, expose

from pydentity.server import ADMIN

class AdminUsersView(BaseView):
    @expose('/')
    def users_list_view(self):
        return self.render('admin/users_list.html')
