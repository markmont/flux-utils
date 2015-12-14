
# Notes on building and running HEASoft on Flux.

## Introduction

HEASoft is a Unified Release of the FTOOLS and XANADU Software Packages.

FTOOLS provides general and mission-specific tools to manipulate FITS files.

XANADU provides high-level, multi-mission tasks for X-ray astronomical spectral, timing, and imaging data analysis.

### Individual installation

HEASoft modifies its own files as it runs, and hence cannot be installed centrally on Flux as a Flux software module.  Each researcher must install their own, personal copy HEASoft in their Flux home directory according to the instructions below.


### HEASoft resources

  * [HEASoft web page](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/).
  * [General HEASoft installation instructions](https://heasarc.gsfc.nasa.gov/lheasoft/install.html).
  * [Fedora/RHEL HEASoft installation notes](https://heasarc.gsfc.nasa.gov/lheasoft/fedora.html).

## Installing HEASoft on Flux

### General setup

Log in to one of the Flux login nodes via SSH and verify that your software module setup is close to standard by running the command `module list`  You should see output that is very close to the following:

```asciidoc
[markmont@flux-login2 ~]$ module list
Currently Loaded Modulefiles:
  1) moab                         4) openmpi/1.6.5/intel/14.0.2
  2) torque                       5) modules
  3) intel-comp/14.0.2            6) use.own
[markmont@flux-login2 ~]$ 
```

If your module list is significantly different from above, adjust it appropriately or contact [hpc-support@umich.edu](mailto:hpc-support@umich.edu) for assistance.

Load the software necessary for compiling HEASoft by running the following commands:

```bash
module unload intel-comp openmpi
module load gcc
```

Choose the directory into which you wish to install HEASoft.  In this example, we will choose a sub-directory named `heasoft` immediately under our home directory.  If you wish to install HEASoft elsewhere, edit the first command below appropriately.  Run:

```bash
export HEASOFT_TOP=~/heasoft
mkdir -p ${HEASOFT_TOP}
cd ${HEASOFT_TOP}
```

NOTE: if you log out of Flux before finishing the install of HEASoft, you will need to run all of the commands in this section again each time you log in to Flux before resuming the install.  Once the installation has been completed, however, it is no longer necessary to run these commands each time you log in to Flux.


### Download and unpack

Visit the [HEASoft download page](http://heasarc.gsfc.nasa.gov/lheasoft/download.html) and fill out the form:

* STEP 1: Select the Source Code distribution and check the "PC - Linux - Red Hat" checkbox.
* STEP 2: Check the "All" checkbox.
* Click the "SUBMIT" button.

The HEASoft source code will download onto your local computer (it may take a while).  After it has downloaded, upload it to Flux and place it in your `~/heasoft` directory.

Then, on Flux, run:

```bash
cd ${HEASOFT_TOP}
mkdir install
tar zxf heasoft-6.17src.tar.gz
```

The `mkdir install` command above is important, as HEASoft will not build (let alone install) if its installation directory does not exist.


### Configure HEASoft

```bash
cd heasoft-6.17/BUILD_DIR
./configure --prefix=${HEASOFT_TOP}/install \
  2>&1 | tee log.configure
grep -i error log.configure
grep -i warn log.configure
```

The following are OK and can be ignored:

```asciidoc
[markmont@flux-login3 BUILD_DIR]$ grep -i error log.configure
checking for strerror... yes
checking for strerror_r... yes
checking for strerror... yes
[markmont@flux-login3 BUILD_DIR]$
```

```asciidoc
markmont@flux-login3 BUILD_DIR]$ grep -i warn log.configure
checking if you want to turn on gcc warnings... no
checking for suffix of module files... configure: WARNING: Could not find Fortran module file extension.
configure: WARNING: not installing docs sun210 sun211
configure: WARNING: Compilation of Fortran wrappers and PGSBOX disabled
configure: WARNING: CFITSIO disabled
configure: WARNING: PGPLOT disabled
configure: WARNING: Compilation of WCS utilities disabled
warning: tcl.h not found with --with-tcl ... tcl build might fail
configure: WARNING: Found Makefile - using build library specs for itcl
configure: WARNING:
[markmont@flux-login3 BUILD_DIR]$
```

### Build HEASoft

```bash
make 2>&1 | tee log.make
grep '\*\*\*' log.make | grep -v 'char \*\*\*'
make install 2>&1 | tee log.install
grep '\*\*\*' log.install
```

### Configure your environment for running HEASoft

Add the following lines near the end of your `~/.bashrc` file:

```bash
export HEADAS=~/heasoft/install/x86_64-unknown-linux-gnu-libc2.12
alias heainit=". ${HEADAS}/headas-init.sh"
```

It is important to not directly source `headas-init.sh` from within your `~/.bashrc` file since doing so will interfere with the Flux software module system and resulting in the `module load` command possibly not working correctly.

Log out of Flux and log back in to get the change to `~/.bashrc` to take effect.  Be sure to re-load the necessary software modules listed at the beginning of this document.

## Using HEASoft

To use HEASoft, log in to a Flux login node, load the `gcc` module, load any additional modules you will be using, and then run `heainit`:

```bash
module unload intel-comp openmpi
module load gcc
heainit
```

You should load all software modules before running `heainit`.  If you load software modules after running `heainit` you may see the following error message and the software modules may not be loaded correctly:

```asciidoc
markmont@flux-login3 flux-utils]$ module load gcc
init.c(573):WARN:162: Cannot initialize TCLX modules using extended commands might fail
init.c(573):WARN:162: Cannot initialize TCLX modules using extended commands might fail
[markmont@flux-login3 flux-utils]$
```

If you see the following error message, it means that you did not load the `gcc` module before running HEASoft:

```asciidoc
xstar: error while loading shared libraries: libquadmath.so.0: cannot open shared object file: No such file or directory
```


## Getting help

If you encounter problems or have questions, please contact [hpc-support@umich.edu](mailto:hpc-support@umich.edu).

