
# Introduction

These are the instructions for installing [CosmoMC](http://cosmologist.info/cosmomc/readme.html) on the [Flux High Performance Computing Cluster](http://arc.research.umich.edu/flux-and-other-hpc-resources/flux/) at the University of Michigan.

CosmoMC is a Markov-Chain Monte-Carlo (MCMC) engine for exploring cosmological parameter space, together with code for analysing Monte-Carlo samples and importance sampling (plus a suite of python scripts for building grids of runs and plotting and presenting results). The code does brute force (but accurate) theoretical matter power spectrum and Cl calculations with CAMB.

CosmoMC appears to work best when each researcher installs their own copy of CosmoMC that they can customize and modify any way they like, rather than trying to share a single centrally-installed copy.

Separate instructions are available on [how to run CosmoMC on Flux](https://github.com/markmont/flux-utils/blob/master/doc/cosmomc/running.md) after it is installed.

If you have any questions or encounter problems, please contact [flux-support@umich.edu](mailto:flux-support@umich.edu) for assistance.


## Additional notes

For generic install instructions for CosmoMC, see http://cosmologist.info/cosmomc/readme.html#Compiling

A relatively recent release of the Intel Fortran compiler is needed to compile CosmoMC; the GNU compilers (gfortran) will not work.  MKL (for LAPACK routines), OpenMPI, and Python are also needed.

*NOTE:* The install instructions below use the Enthought Python Distribution (EPD) version of Python; this consideribly simplifies the install since EPD already includes numpy, pylab, matplotlib, cython, h5py, and pyfits.  However, EPD is compiled using non-Intel compilers, which could cause run-time problems for CosmoMC or Planck Likelihood python modules that interface to C libraries. If a CosmoMC or Planck Likelihood Python module fails to run, please report it to [flux-support@umich.edu](mailto:flux-support@umich.edu) together with a test case for reproducing the problem.  It may be possible to adjust the install procedure slightly to work around this problem; in the worst case, we can provide instructions for compiling a special version of Python and the necessary 3rd-party Python modules (numpy, et al.) using the Intel compilers for use by CosmoMC.

# General setup

Log in to one of the Flux login nodes via SSH and verify that your software module setup is close to standard by running the command `module list`  You should see output that is very close to the following:

```asciidoc
[markmont@flux-login2 ~]$ module list
Currently Loaded Modulefiles:
  1) moab                       4) openmpi/1.6.0/intel/12.1
  2) torque                     5) modules
  3) intel-comp/12.1            6) use.own
[markmont@flux-login2 ~]$ 
```

If your module list is significantly different from above, adjust it appropriately or contact [flux-support@umich.edu](mailto:flux-support@umich.edu) for assistance.

Load the software necessary for compiling CosmoMC by running the following commands:

```bash
module unload intel-comp
module unload openmpi
module unload gcc gsl hdf5 cfitsio
module unload python anaconda epd
module load intel-comp/14.0.2
module load mkl/10.3.7
module load openmpi/1.8.1/intel/14.0.2
module load epd/7.3-2a
```

After loading the above software modules, the `module list` command output should look like

```asciidoc
[markmont@flux-login2 ~]$ module list
Currently Loaded Modulefiles:
  1) moab                         5) intel-comp/14.0.2
  2) torque                       6) mkl/10.3.7
  3) modules                      7) openmpi/1.8.1/intel/14.0.2
  4) use.own                      8) epd/7.3-2a
[markmont@flux-login2 ~]$ 
```

Choose the directory into which you wish to install CosmoMC and all of its associated dependencies.  In this example, we will choose a sub-directory named `cosmomc-201405a` immediately under our home directory.  If you wish to install CosmoMC elsewhere, edit the fist command below appropriately.  Run:

```bash
export COSMOMC_TOP=~/cosmomc-201405a
mkdir -p ${COSMOMC_TOP}
cd ${COSMOMC_TOP}
```

*NOTE:* if you log out of Flux before finishing the install of CosmoMC, you will need to run all of the commands in this section again each time you log in to Flux before resuming the install.


# Download and unpack

Make sure you are in the correct directory:

```bash
cd ${COSMOMC_TOP}
```

## Download CosmoMC directly onto Flux

Fill out the following form to get the download link in the command below: http://cosmologist.info/cosmomc/submit.html

Right click the very first link on the download page (the link says "download"), select "Copy link location", and paste the result into the command below.

```bash
wget PASTE_THE_COPIED_URL_HERE
```

## Download the Planck Likelihood code and data

You can get updated URLs, if needed, by right-clicking the links at http://www.sciops.esa.int/wikiSI/planckpla/index.php?title=CMB_spectrum_%26_Likelihood_Code&instance=Planck_Public_PLA#Likelihood_4

```bash
wget http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_Code_Likelihood-v1.0_R1.10.tar.gz
wget http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-commander_R1.10.tar.gz
wget http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-lowlike_R1.10.tar.gz
wget http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-CAMspec_R1.10.tar.gz
wget http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-actspt_R1.10.tar
wget http://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-lensing_R1.10.tar.gz
```

Note that the second to last file above is missing the `.gz` from the end; this is not incorrect.


## Download HEALPix

You can update the URL below by going to http://healpix.sourceforge.net/downloads.php

We specify the output file name using the `-O` option, otherwise the file would be named `download`.

```bash
wget -O Healpix_3.11_2013Apr24.tar.gz http://sourceforge.net/projects/healpix/files/Healpix_3.11/Healpix_3.11_2013Apr24.tar.gz/download
```

## Unpack everything

You should now see the following when you run `ls -l`:

```asciidoc
[markmont@flux-login2 cosmomc-201405a]$ ls -l
total 1213324
-rw------- 1 markmont lsa  38750016 May 14 04:54 cosmomc.tar.gz
-rw------- 1 markmont lsa  24256278 Apr 24  2013 Healpix_3.11_2013Apr24.tar.gz
-rw------- 1 markmont lsa    502226 Jul 11 15:37 product-action?COSMOLOGY.FILE_ID=COM_Code_Likelihood-v1.0_R1.10.tar.gz
-rw------- 1 markmont lsa 260853760 Jul 11 15:41 product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-actspt_R1.10.tar
-rw------- 1 markmont lsa 388620967 Jul 11 15:40 product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-CAMspec_R1.10.tar.gz
-rw------- 1 markmont lsa  37979357 Jul 11 15:37 product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-commander_R1.10.tar.gz
-rw------- 1 markmont lsa    134074 Jul 11 15:41 product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-lensing_R1.10.tar.gz
-rw------- 1 markmont lsa 486426096 Jul 11 15:39 product-action?COSMOLOGY.FILE_ID=COM_Data_Likelihood-lowlike_R1.10.tar.gz
[markmont@flux-login2 cosmomc-201405a]$ 
```

### Unpack all the code

Unpacking the Plank Likelihood code will result in a new file, `plc-1.0.tar.bz2` which itself needs to be unpacked.

```bash
tar zxf cosmomc.tar.gz
tar zxf Healpix_3.11_2013Apr24.tar.gz
tar zxf *COM_Code_*
tar jxf plc-1.0.tar.bz2
```

### Unpack the Planck Likelihood data

The Planck Likelihood data needs to be installed inside the Planck likelihood code directory, under the subdirectory `share/clik`

Adjust the version number of the Planck Likelihood code directory below if you unpacked a verion other than 1.0.

```bash
gzip -d *COM_Data_*.gz
mkdir -p plc-1.0/share/clik
cd plc-1.0/share/clik
for filename in ${COSMOMC_TOP}/*COM_Data_*.tar ; do
  echo $filename
  tar xf $filename
done
```


# Install Planck Likihood code and data

The Planck Likelihood code and data is used to compute the likelihood of a model that predicts the CMB power spectra, lensing power spectrum, together with some foreground and some instrumental parameters. The data files are built primarily from the Planck mission results, but include also some results from the WMAP-9 data release.

Vendor website: http://www.sciops.esa.int/wikiSI/planckpla/index.php?title=CMB_spectrum_%26_Likelihood_Code&instance=Planck_Public_PLA#Likelihood_4
See also: http://cosmologist.info/cosmomc/readme_planck.html
See also: http://cosmologist.info/cosmomc/readme.html#Compiling


Make sure the EPD version of Python will be used, *not* `/usr/bin/python`.  The correct path is `/home/software/rhel6/epd/7.3-2a/bin/python`.  If the following command reports `/usr/bin/python`, do the steps in the "General setup" section, above.

```bash
which python
```

In the future, it may be desirable to install GSL before installing the Planck Likelihood code.  GSL is already installed on Flux, but it looks like the versions that are installed are only for the GNU compiler; we'd need to recompile them for use with the Intel compilers instead.

In the future, it may also be desirable to install [pmclib](http://www2.iap.fr/users/kilbinge/CosmoPMC/) and/or BoPix.

Currently, CosmoMC appears to be functioning fine without GSL, pmclib, or BoPix.

Note: the `--install_all_deps` option to `waf` is not actually installing all dependencies, so we list each depenency manually.

Note: the `--healpix_install` option to `waf` doesn't do anything unless BoPix is already installed, so we will install HEALPix manually later.  Although HEALPix will not be used by the Planck Likelihood code (since BoPix is not installed), HEALPix is required by CosmoMC itself.

*IMPORTANT NOTE:* Make sure to invoke `waf` by running `python ./waf` rather than by typing `waf` or `./waf`.  This is necessary in order to ensure that the Planck Likelihood code finds the correct version of Python which includes Numpy and the other Python modules that the Planck Likelihood code requires.

```bash
cd ${COSMOMC_TOP}/plc-1.0
python ./waf configure --icc --ifort --install_all_deps --hdf5 --hdf5_install --cfitsio_install --wmap_install --lapack_mkl=${MKLROOT} --lapack_mkl_version=10.3 2>&1 | tee log.configure
python ./waf install 2>&1 | tee log.install
```

# Install HEALPix

In the future, we might want to install PGPLOT before installing HEALPix.  Currently, HEALPix is getting installed without PGPLOT support.  For assistance, please contact [flux-support@umich.edu](mailto:flux-support@umich.edu).

HEALPix uses an interactive configuration process.  Run the commands immediately below, and then respond with the answers that follow.

```bash
cd ${COSMOMC_TOP}/Healpix_3.11
./configure -L
```

Don't configure the IDL package (CosmoMC doesn't use IDL).

First select the C package (option 2) and respond with the following.  Note that it will ask you at the end if you want to modify your shell profile -- make sure you respond negatively, as HealPix won't make the correct modifications for Flux (we'll make the correct modifications manually later on).

If you see no response on a given line (the line ends with a colon), just press RETURN for that line to accept the default value.

Make sure you manually replace XXXxxxXXX in the responses below with the location where you are installing CosmoMC.  For example, if you see `XXXxxxXXX/plc-1.0/lib` in a response below, you'd actually type something like `/home2/markmont/cosmomc-201405a/plc-1.0/lib` there instead.

```asciidoc
Enter your choice (configuration of packages can be done in any order): 2
Warning: The following directories could not be found:
/home2/markmont/cosmomc-201405a/Healpix_3.11/include
/home2/markmont/cosmomc-201405a/Healpix_3.11/lib
Should I attempt to create these directories (Y|n)? 
enter C compiler you want to use (gcc): icc
enter options for C compiler (-O2 -Wall): -O2 -std=gnu99
enter archive creation (and indexing) command (ar -rsv): xiar -rsv
enter full name of cfitsio library (libcfitsio.a): 
enter location of cfitsio library (/usr/local/lib): XXXxxxXXX/plc-1.0/lib
enter location of cfitsio header fitsio.h (/home2/markmont/cosmomc-201405a/plc-1.0/include): 
A static library is produced by default. Do you also want a shared library ?(y|N) 
```

```asciidoc
The following line should be inserted into your home shell profile (/home2/markmont//.profile):

  [ -r /home2/markmont/cosmomc-201405a/Healpix_3.11/confdir/3_11_Linux/config ] && . /home2/markmont/cosmomc-201405a/Healpix_3.11/confdir/3_11_Linux/config

 Where the file /home2/markmont/cosmomc-201405a/Healpix_3.11/confdir/3_11_Linux/config contains:
# configuration for Healpix 3.11
HEALPIX=/home2/markmont/cosmomc-201405a/Healpix_3.11 ; export HEALPIX 
HPX_CONF_DIR=/home2/markmont/cosmomc-201405a/Healpix_3.11/confdir/3_11_Linux
if [ -r ${HPX_CONF_DIR}/idl.sh ] ; then . ${HPX_CONF_DIR}/idl.sh ; fi
if [ -r ${HPX_CONF_DIR}/f90.sh ] ; then . ${HPX_CONF_DIR}/f90.sh ; fi
if [ -r ${HPX_CONF_DIR}/cpp.sh ] ; then . ${HPX_CONF_DIR}/cpp.sh ; fi
if [ -r ${HPX_CONF_DIR}/c.sh ] ;   then . ${HPX_CONF_DIR}/c.sh ;   fi

Do you want this modification to be done (y|N)? N
```

Next, configure the F90 package (option 3):

```asciidoc
Enter your choice (configuration of packages can be done in any order): 3
you seem to be running Linux
enter name of your F90 compiler (): ifort
  Note: your Fortran compiler is Intel Fortran Compiler
  compiled Healpix products will be:
F90_BINDIR =  ./bin[suffix]
F90_INCDIR =  ./include[suffix]
F90_LIBDIR =  ./lib[suffix]
enter suffix for directories (): 
 compiled Healpix products will be:
F90_BINDIR =  ./bin
F90_INCDIR =  ./include
F90_LIBDIR =  ./lib
Warning: The following directories could not be found:
./bin
Should I attempt to create these directories (Y|n)? 
 enter compilation flags for ifort compiler (-I$(F90_INCDIR) -cm -w -vec_report0 -sox): 
enter optimisation flags for ifort compiler (-O3): -O2
  Fortran code will be compiled with ifort -O2 -std=gnu99 -I$(F90_INCDIR) -cm -w -vec_report0 -sox
enter name of your C compiler (cc): icc
enter compilation/optimisation flags for C compiler (-O3 -std=c99 -DINTEL_COMPILER): -O2 -std=gnu99 -DINTEL_COMPILER
  C subroutines will be compiled with icc -O2 -std=gnu99 -DINTEL_COMPILER
enter command for library archiving (ar -rsv): xiar -rsv
enter full name of cfitsio library (libcfitsio.a): 
enter location of cfitsio library (/home2/markmont/cosmomc-201405a/plc-1.0/lib): 
  The generator of non-gaussian CMB maps (ng_sims) can optionally 
produce plots of the maps Prob. Dens. Function using PGPLOT.
Do you want to enable this option ? 
(this assumes that PGPLOT is already installed on your computer) (y|N)

 The Spherical Harmonics Transform (C and F90) routines used by 
synfast/anafast/smoothing/plmgen
and some routines used by ud_grade and alteralm respectively
have a parallel implementation (based on OpenMP).
Do you want to use :
 0) the standard serial implementation ?
 1) the parallel implementation 
Enter choice                                      (1): 
 
 Do you want a Position Independent Compilation  (option  "-fPIC") 
(recommended if the Healpix-F90 library is to be linked to external codes)  (Y|n): 
Generating /home2/markmont/cosmomc-201405a/Healpix_3.11/confdir/3_11_Linux/f90.sh
Editing top Makefile for F90 ... done.
```

Now configure the C++ package (option 4):

```asciidoc
Enter your choice (configuration of packages can be done in any order): 4
enter location of cfitsio library (/home2/markmont/cosmomc-201405a/plc-1.0/lib): 
enter location of cfitsio header fitsio.h (/home2/markmont/cosmomc-201405a/plc-1.0/include):
Available configurations for C++ compilation are:
   1: basic_gcc
   2: generic_gcc
   3: linux_icc
   4: osx
   0: None of the above (will send you back to main menu).
   You can create your own C++ configuration in /home2/markmont/cosmomc-201405a/Healpix_3.11/src/cxx/config/config.* 
Choose one number: 3
will compile with linux_icc configuration
Generating /home2/markmont/cosmomc-201405a/Healpix_3.11/confdir/3_11_Linux/cpp.sh
edit top Makefile for C++ ... done.
```

Do not configure the Python (healpy) package, as CosmoMC does not import it, and configuring it will cause the error described at https://github.com/healpy/healpy/issues/102  While it is possible to resolve this error, there is currently no need to do so.

Now build and install HEALPix by running the following commands:

```bash
make 2>&1 | tee log.make
make test 2>&1 | tee log.test
```

All 10 tests should succeed.


# Install CosmoMC

Make the Planck Liklihood data accessible to CosmoMC.  When you run the `ls click` command below, make sure you see the various data sets (actspt, CAMspec, commander, lowlike, and liening_likelihood).

```bash
cd ${COSMOMC_TOP}/cosmomc/data
ln -s ../../plc-1.0/share/clik clik
ls click
```

Run the following commands so that CosmoMC can find everything it needs in order to build.  Do not put these commands in your `.bashrc` file at this point, since a few more things will be needed after building CosmoMC in order to run CosmoMC.

```bash
source ${COSMOMC_TOP}/Healpix_3.11/confdir/3_11_Linux/config
export CLIK_DATA=${COSMOMC_TOP}/plc-1.0/share/clik
export PYTHONPATH=${COSMOMC_TOP}/plc-1.0/lib/python2.7/site-packages:${PYTHONPATH}
export PLANCKLIKE=cliklike
export CLIKPATH=${COSMOMC_TOP}/plc-1.0
export PATH=${CLIKPATH}/bin:${PATH}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${CLIKPATH}/lib
```

```bash
cd ${COSMOMC_TOP}/cosmomc/camb
```

Edit the file `Makefile_main` (inside the directory above).  About 80% of the way through the file, you will see two lines that read:

```asciidoc
$(CAMBLIB): $(CAMBOBJ)
        ar -r $@ $(CAMBOBJ)
```

Change the `ar -r` on the second line above to be `xiar -rs`.  Be careful to not change the indentation of that line (the line must have a single tab character at the beginning; anything else, including spaces will cause the file to not work).

```bash
cd ${COSMOMC_TOP}/cosmomc/source
```

Edit the file `Makefile` in this second directory.  Find the `FFLAGS` line near the top of the file.  Change it from

```asciidoc
FFLAGS = -mkl -openmp -O3 -xHost -no-prec-div -fpp
```

to
```asciidoc
FFLAGS = -mkl -openmp -O2 -no-prec-div -fpp
```

(that is, change `-O3` to be `-O2` and also remove `-xHost` from the line).

Finally, build CosmoMC:

```bash
cd ${COSMOMC_TOP}/cosmomc
make all cfitsio=${CLIKPATH} 2>&1 | tee log.make
```

# Create setup script

It will be useful to have a way to easily set up all of the shell environment variables needed to run CosmoMC.  Having this in a separate, dedicated file will allow the set up to be done from where ever it is needed, including from the command line, in PBS scripts, or in shell dot files.

Create a file named `cosmomc-setup.sh` in the `${COSMOMC_TOP}` directory containing the following.  Be sure to change the value on the first line to reflect the same path you chose for COSMOMC_TOP in the "General setup" section of these installation notes, above.

```bash
export COSMOMC_TOP=~/cosmomc-201405a
export COSMOMC=${COSMOMC_TOP}/cosmomc
source ${COSMOMC_TOP}/Healpix_3.11/confdir/3_11_Linux/config
export PYTHONPATH=${COSMOMC_TOP}/plc-1.0/lib/python2.7/site-packages:${PYTHONPATH}
export PLANCKLIKE=cliklike
export CLIKPATH=${COSMOMC_TOP}/plc-1.0
export CLIK_DATA=${CLIKPATH}/share/clik
export PATH=${COSMOMC}:${COSMOMC_TOP}/plc-1.0/bin:${PATH}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${CLIKPATH}/lib
```

# Logout

*IMPORTANT!* After you are done building CosmoMC, log out of Flux.  Building CosmoMC has made changes to your shell environment that can cause problems if you immediately attempt to run CosmoMC.  Logging out of Flux and then logging back in will reset these changes and provide you with a clean shell environment from which you can safely run CosmoMC.


Instructions how to run CosmoMC on Flux are available at https://github.com/markmont/flux-utils/blob/master/doc/cosmomc/running.md
