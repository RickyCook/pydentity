#!/usr/bin/env python
from distutils.version import LooseVersion
from setuptools import setup

REQUIREMENT_ERROR_FS = "%s is required to install pydentity"

try:
    from pip.req import parse_requirements
except ImportError:
    raise Exception(REQUIREMENT_ERROR_FS % "Pip")

try:
    import samba
    assert LooseVersion(samba.version) >= LooseVersion("4.0.0")
except ImportError:
    raise Exception(REQUIREMENT_ERROR_FS % "Samba Python bindings >= 4.0.0")

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_requires = [str(requirement.req)
                    for requirement
                    in parse_requirements('requirements.txt')]

setup(name="pydentity",
      version="0.0.1",
      description="Simple identity server for the web",
      author="Ricky Cook",
      author_email="mail@thatpanda.com",
      py_modules=['pydentity', 'pydentity.server'],
      scripts=['pydentity_server'],
      install_requires=['pip'] + install_requires,
      )
