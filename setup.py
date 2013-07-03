#!/usr/bin/env python

# Copyright, 2012-2013 AOL Inc.

from setuptools import setup, find_packages, Command
import glob
import os
import sys
import unittest

# Get version from pkg index
from pwswimmeets import __version__
from pwswimmeets import __author__
from pwswimmeets import __maintainer__
from pwswimmeets import __email__
from pwswimmeets import __doc__


# Names of required packages
requires = [
]

class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system ('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

desc = ''
long_desc = '''
'''

setup(
    name='pwswimmeets',
    version=__version__,
    author=__author__,
    author_email=__email__,
    packages=find_packages(exclude=['tests']),
    license='',
    url='',
    description=desc,
    long_description=long_desc,
    scripts=[],
    include_package_data=True,
    install_requires=requires,
    keywords = [
        'swim'
    ],
    classifiers = [
    ],
    cmdclass={
        'clean': CleanCommand
    }
)
