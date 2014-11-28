import re

SYSTEM_PROPERTY_RE = re.compile(r'^__(.+)__$')
SIMPLE_PRINTABLE_TYPES = (str, unicode, int, long, float)
