ABOUT
=====

`flux-utils` -- Miscellaneous utlities for use on the Flux HPC cluster at the University of Michigan


SYNOPSIS
========

freealloc - displays unused cores and memory for an allocation

    freealloc [-h] [--jobs] allocation_name


INSTALLATION
============

flux-utils requires either Python 3 or, if Python 2 is being used, the `argparse` module.


The following commands are very rough and are specific to Flux:

```bash
mkdir /usr/flux/software/src/lsa/flux-utils
cd /usr/flux/software/src/lsa/flux-utils

INSTALL_DIR=/home/software/rhel6/lsa/flux-utils

mkdir -p ${INSTALL_DIR}/python-modules/lib/python2.6/site-packages/


# Only needed for Python 2 < 2.7
# or Python 3 < 3.2
#
# We don't want to force the use of a specific install of python, since
# this could interefere with software modules the user chooses to load.
# So instead we use whatever comes first in the user's PATH.  If the user
# has not loaded anything, we'll get the standard RHEL version of Python 2.6.2 
# which does not come with argparse.

wget http://argparse.googlecode.com/files/argparse-1.2.1.tar.gz
tar zxf argparse-1.2.1.tar.gz
cd argparse-1.2.1
python ./setup.py build 2>&1 | tee log.build
PYTHONPATH=${INSTALL_DIR}/python-modules/lib/python2.6/site-packages/ \
  python ./setup.py install --prefix ${INSTALL_DIR}/python-modules \
  2>&1 | tee log.install
cd .


mkdir ${INSTALL_DIR}/bin
cp ~markmont/flux-utils/freealloc .
cp freealloc ${INSTALL_DIR}/bin
chmod 755 ${INSTALL_DIR}/bin/freealloc


mkdir /home/software/rhel6/lsa/Modules/modulefiles/flux-utils/
cp -r /home/software/rhel6/lsa/Modules/modulefiles/pgplot/* \
  /home/software/rhel6/lsa/Modules/modulefiles/flux-utils/
cd /home/software/rhel6/lsa/Modules/modulefiles/flux-utils
mv pgplot.inc.tcl flux-utils.inc.tcl
mv 5.2.2/g77 1
rmdir 5.2.2

vi /home/software/rhel6/lsa/Modules/modulefiles/flux-utils/flux-utils.inc.tcl
   # Make any changes needed

vi /home/software/rhel6/lsa/Modules/modulefiles/flux-utils/1
   # Make any changes needed


cp BUILD_NOTES-flux-utils ${INSTALL_DIR}

# Set permissions so that lsaswadm can administer:
for d in ${INSTALL_DIR} \
  /home/software/rhel6/lsa/Modules/modulefiles/flux-utils \
  /usr/flux/software/src/lsa/flux-utils ; do
  chgrp -R lsaswadm $d
  chmod -R g+rwX,o+rX $d
  find $d -type d | xargs chmod g+s
done

```


SUPPORT
=======

Please send any questions, feedback, requests, or patches to markmont@umich.edu

Additional resources may be available at [http://github.com/markmont/flux-utils](http://github.com/markmont/flux-utils)


LICENSE
=======

`flux-utils` is Copyright (C) 2013 Regents of The University of Michigan.

`flux-utils` is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

`flux-utils` is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with `flux-utils`.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)

