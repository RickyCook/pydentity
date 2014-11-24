#!/usr/bin/env python
from setuptools import setup

try:
    from pip.req import parse_requirements
except ImportError:
    raise Exception("Pip is required to install pydentity")

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
      install_requires=install_requires,
      )
