import importlib
import logging
import re
import urllib

from flask import redirect, url_for
from flask.ext.admin import BaseView, expose

IGNORED_OBJECT_NAMES = ('__builtins__',)
BUILTIN_TYPES = (str, unicode, int, long, float, type(None))
SYSTEM_PROPERTY_RE = re.compile(r'^__(.+)__$')

def group_attrs(obj):
    """
    Group attributes on obj by type, returning a tuple of meta attributes, and
    grouped attributes
    """
    attr_names = dir(obj)

    meta = {}
    groups = {}
    for attr_name in attr_names:
        if attr_name in IGNORED_OBJECT_NAMES:
            continue

        try:
            attr = getattr(obj, attr_name)
        except AttributeError:
            logging.exception("Couldn't get '%s' attribute from '%s'",
                              attr_name, obj.__name__)
            continue

        system_property_match = SYSTEM_PROPERTY_RE.match(attr_name)

        if system_property_match:
            attr_type = type(attr)
            if attr_type in BUILTIN_TYPES:
                meta[system_property_match.groups()[0]] = attr
            else:
                groups.setdefault('... more', []).append(attr_name)
        else:
            attr_type_name = type(attr).__name__
            group = groups.setdefault(attr_type_name, [])
            group.append(attr_name)

    return meta, groups

class DebugAPIBrowseView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('.module_detail', module_name='samba'))

    @expose('/<string:module_name>')
    def module_detail(self, module_name):
        root_object = importlib.import_module(module_name)
        object_meta, grouped_attrs = group_attrs(root_object)

        return self.render('admin/debug/api_browse.html',
                           module_name=module_name,
                           object_meta=object_meta,
                           grouped_attrs=grouped_attrs,
                           )

    @expose('/<string:module_name>/<path:object_path>')
    def attr_detail(self, module_name, object_path):
        root_object = importlib.import_module(module_name)

        object_path_arr = object_path.split('/')

        for path_segment in filter(bool, object_path_arr):
            root_object = getattr(root_object, path_segment)

        object_meta, grouped_attrs = group_attrs(root_object)

        return self.render('admin/debug/api_browse.html',
                           module_name=module_name,
                           object_path=object_path,
                           object_meta=object_meta,
                           grouped_attrs=grouped_attrs,
                           )
