
from flask.ext.admin import BaseView, expose

class AdminObjectsListView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/objects_list.html', endpoint=self.endpoint)
