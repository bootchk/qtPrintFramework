#!/usr/bin/env python

from distutils.core import setup

setup(name='qtPrintFramework',
      version='0.1',
      description='Print subsystem wrapping Qt print system',
      author='Lloyd Konneker',
      author_email='bootch@nc.rr.com',
      url='https://github.com/bootchk/qtPrintFramework',
      packages=['qtPrintFramework',
                'qtPrintFramework.model',
                'qtPrintFramework.userInterface',
                'qtPrintFramework.paper', ]
     )