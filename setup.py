#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'arc-utils',
    version = '1.0',
    description = 'ARC Cluster Utilities',
    author = 'Mark Montague',
    author_email = 'markmont@umich.edu',
    url = 'http://github.com/markmont/flux-utils',
    packages = [ 'torque' ],
    scripts = [ 'freealloc', 'lsa_flux_check', 'cancel-my-jobs' ],
    )

