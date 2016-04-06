ABOUT
=====

`flux-utils` -- Miscellaneous utlities for use on the Flux HPC cluster at the University of Michigan


SYNOPSIS
========

`freealloc` - displays unused cores and memory for an allocation

    freealloc [-h] [--jobs] allocation_name


`lsa_flux_check` - checks to see if a user is complying with the usage limits for the LSA public Flux allocaitons

    lsa_flux_check [-h] [--all] [--details] [--mail] [--daemonize] [--submit]

    optional arguments:
      -h, --help   show this help message and exit
      --all        check the usage of all users
      --details    display extra information
      --mail       send mail to offending users (Flux support staff only)
      --daemonize  run as a daemon (Flux support staff only)
      --submit     run as a self-resubmitting job (Flux support staff only)


`gpujobinfo` - displays information about jobs requesting GPUs

    gpujobinfo


`arclogs` - retrieves log entries for a job

    arclogs [--days N] job_id

    optional arguments:
      -h, --help   show this help message and exit
      --days N     search the most recent N days of logs (default: 1)


INSTALLATION
============

`flux-utils` requires:

* [TORQUE](http://www.adaptivecomputing.com/products/open-source/torque/)
* [python-daemon](https://pypi.python.org/pypi/python-daemon)
* argparse (included with Python 2.7 and later, and with Python 3.2 and later)
* `arclogs` requires Perl 5 and `cpan`

The following commands are very rough and are specific to Flux:

```bash
mkdir /usr/flux/software/src/lsa/flux-utils
cd /usr/flux/software/src/lsa/flux-utils

git clone https://github.com/markmont/flux-utils.git
cd flux-utils

export INSTALL_DIR=/usr/cac/rhel6/lsa/flux-utils
mkdir -p ${INSTALL_DIR}/lib/python2.6/site-packages/

PYTHONPATH=${INSTALL_DIR}/lib/python2.6/site-packages/ \
  easy_install --prefix ${INSTALL_DIR} argparse python-daemon \
  2>&1 | tee log.install

python ./setup.py build 2>&1 | tee log.build
PYTHONPATH=${INSTALL_DIR}/lib/python2.6/site-packages/ \
  python ./setup.py install --prefix ${INSTALL_DIR} \
  2>&1 | tee -a log.install


mkdir /usr/cac/rhel6/lsa/Modules/modulefiles/flux-utils/
cp -r /usr/cac/rhel6/lsa/Modules/modulefiles/pgplot/* \
  /usr/cac/rhel6/lsa/Modules/modulefiles/flux-utils/
cd /usr/cac/rhel6/lsa/Modules/modulefiles/flux-utils
mv pgplot.inc.tcl flux-utils.inc.tcl
mv 5.2.2/g77 1
rmdir 5.2.2

vi /usr/cac/rhel6/lsa/Modules/modulefiles/flux-utils/flux-utils.inc.tcl
   # Make any changes needed

vi /usr/cac/rhel6/lsa/Modules/modulefiles/flux-utils/1
   # Make any changes needed


cp BUILD_NOTES-flux-utils ${INSTALL_DIR}

# Set permissions so that lsaswadm can administer:
for d in ${INSTALL_DIR} \
  /usr/cac/rhel6/lsa/Modules/modulefiles/flux-utils \
  /usr/flux/software/src/lsa/flux-utils ; do
  chgrp -R lsaswadm $d
  chmod -R g+rwX,o+rX $d
  find $d -type d | xargs chmod g+s
done

```

To set up `arclogs`:

```bash

export INSTALL_DIR=/usr/cac/rhel6/lsa/arc-admin-utils

rm -rf ~/.cpan
script cpan-setup.log
  perl -MCPAN -e shell
    # if it asks you if you want it to configure as much as possible, say "yes"
    o conf makepl_arg PREFIX=/usr/cac/rhel6/lsa/arc-admin-utils/perl5
    o conf mbuildpl_arg "--prefix /usr/cac/rhel6/lsa/arc-admin-utils/perl5"
    o conf prerequisites_policy follow
    o conf build_requires_install_policy yes
    o conf commit
    quit
exit

script cpan-elasticsearch.log
  export PERL5LIB=${INSTALL_DIR}/perl5/lib64/perl5:${INSTALL_DIR}/perl5/share/perl5
  cpan
    install Search::Elasticsearch
    quit
exit

```


SUPPORT
=======

Please send any questions, feedback, requests, or patches to markmont@umich.edu

Additional resources may be available at [http://github.com/markmont/flux-utils](http://github.com/markmont/flux-utils)


LICENSE
=======

`flux-utils` is Copyright (C) 2013 - 2016 Regents of The University of Michigan.

`flux-utils` is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

`flux-utils` is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with `flux-utils`.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)

