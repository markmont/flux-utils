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
exec newgrp lsaswadm
umask 0002

sudo mkdir /usr/local/flux-utils
sudo chown ${USER}:lsaswadm /usr/local/flux-utils
sudo chmod 2775 /usr/local/flux-utils

git clone https://github.com/markmont/flux-utils.git
cd flux-utils

export INSTALL_DIR=/usr/local/flux-utils
mkdir -p ${INSTALL_DIR}/lib/python2.7/site-packages/

python ./setup.py build 2>&1 | tee log.build

# Use "--single-version-externally-managed --record /dev/null" to force
# setuptools to not wrap the Python scripts.  Wrapping the scripts fails
# since the flux-utils modifies its own PYTHONPATH (the wrappers don't know
# where to look to find the actual scripts).

PYTHONPATH=${INSTALL_DIR}/lib/python2.7/site-packages/ \
  python ./setup.py install --single-version-externally-managed \
  --record /dev/null --prefix ${INSTALL_DIR} \
  2>&1 | tee log.install

# .../flux-utils/bin is in users' default PATH, but /sw/med/centos7 is not
# so create a symlink to make tto and maxwalltime available:
( cd ${INSTALL_DIR}/bin ;
  ln -s /sw/med/centos7/tto ;
  ln -s /sw/med/centos7/tto maxwalltime )

# .../flux-utils/bin is in users' default PATH, but /usr/arc-connect is not
# so create a symlink to make the VNC scripts available:
( cd ${INSTALL_DIR}/bin ;
  for v in /usr/arc-connect/flux/centos7/bin/vnc-* ; do
    ln -s $v
  done )


mkdir socks
cd socks
# Download the Dante source code from http://www.inet.no/dante/download.html
wget http://www.inet.no/dante/files/dante-1.4.1.tar.gz
tar zxf dante-1.4.1.tar.gz
cd dante-1.4.1
./configure --prefix=${INSTALL_DIR} \
  --with-socks-conf=${INSTALL_DIR}/etc/socks.conf \
  2>&1 | tee log.socks.configure
make 2>&1 | tee log.socks.make
make install 2>&1 | tee log.socks.install
mkdir -p ${INSTALL_DIR}/etc
cat > ${INSTALL_DIR}/etc/socks.conf <<__EOF__
resolveprotocol: tcp  # work around ssh proxying only TCP, not needed if using a real SOCKS server
route {
        from: 0.0.0.0/0 to: 0.0.0.0/0 via: 127.0.0.1 port = 1080
        proxyprotocol: socks_v4 socks_v5
        method: none
}
__EOF__


# Set permissions so that lsaswadm can administer:
chmod -R g+rwX,o+rX ${INSTALL_DIR}
find ${INSTALL_DIR} -type d | xargs chmod g+s
sudo chown -R root:lsaswadm ${INSTALL_DIR}

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

