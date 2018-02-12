#!/usr/bin/env python

from distutils.core import setup

setup(name='Surfjudge',
      version='1.0',
      description='Surfjudge Software',
      author='Dario Goetz',
      author_email='dario.goetz@googlemail.com',
      packages=['surfjudge'],
      install_requires=['cherrypy', 'bcrypt', 'jinja2', 'configobj', 'sqlalchemy'],
     )
