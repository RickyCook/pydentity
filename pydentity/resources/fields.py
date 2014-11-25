from urllib import urlencode

from flask.ext.restful import fields

class UrlQS(fields.Url):
    """
    Much line a Flask-restful Url field, but adds object as URL query string
    arguments instead of url_for params
    """
    def output(self, key, obj):
        output = super(UrlQS, self).output(key, obj)

        if key in obj:
            return "%s?%s" % (output, urlencode(obj[key]))
        else:
            return output
