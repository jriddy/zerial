#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://zerial.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='zerial',
    version='0.0.6',
    description='Stuct and destructure complex classes',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Josh Reed',
    author_email='jriddy@gmail.com',
    url='https://github.com/jriddy/zerial',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'attrs',
        'typing;python_version<"3.5"',
    ],
    license='MIT',
    zip_safe=False,
    keywords='zerial',
    classifiers=[
        # Some troves are left commented out because I intend to support those
        # versions eventually.
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: Implementation :: PyPy',
    ],
    extras_require={
        'tests': [
            'pytest',
            'pytest-mock',
            'flake8',
        ],
        'docs': [
            'sphinx',
        ],
        'release': [
            'bump2version',
        ],
    }
)
