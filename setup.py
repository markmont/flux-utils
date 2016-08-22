#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'flux-utils',
    version = '1.0',
    description = 'ARC-TS Cluster Utilities',
    author = 'Mark Montague',
    author_email = 'markmont@umich.edu',
    license = 'GPL3',
    url = 'http://github.com/markmont/flux-utils',
    install_requires = [ 'python-daemon' ],
    packages = [ 'torque' ],
    scripts = [ 'freenodes', 'freealloc', 'lsa_flux_check', 'cancel-my-jobs', 'idlenodes' ],
    )

