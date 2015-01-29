#!/usr/bin/env python

from distutils.core import setup

setup(name='qtPrintFramework',
      version='0.1',
      description='Print subsystem wrapping Qt print system',
      author='Lloyd Konneker',
      author_email='bootch@nc.rr.com',
      url='https://github.com/bootchk/qtPrintFramework',
      packages=['qtPrintFramework',
                'qtPrintFramework.converser',
                'qtPrintFramework.pageLayout',
                'qtPrintFramework.pageLayout.able',
                'qtPrintFramework.pageLayout.components',
                'qtPrintFramework.pageLayout.components.paper',
                'qtPrintFramework.pageLayout.model',
                'qtPrintFramework.printer',
                'qtPrintFramework.userInterface',
                'qtPrintFramework.userInterface.qml',
                'qtPrintFramework.userInterface.qml.dialog',
                'qtPrintFramework.userInterface.widget',
                'qtPrintFramework.userInterface.widget.dialog',
                ]
     )