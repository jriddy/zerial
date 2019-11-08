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

numpy_require = ['numpy']
tests_require = [
    'pytest',
    'pytest-mock',
    'flake8',
]
docs_require = ['sphinx']
release_require = ['bump2version']

dev_require = numpy_require + tests_require + docs_require + release_require


setup(
    name='zerial',
    version='0.2.1',
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
        'enum;python_version<"3.4"',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: Implementation :: PyPy',
    ],
    extras_require={
        'numpy': numpy_require,
        'tests': tests_require + numpy_require,
        'docs': docs_require,
        'release': release_require,
        'dev': dev_require,
    },
)
