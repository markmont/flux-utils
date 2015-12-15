
# Notes on running pvm_xstar on Flux

## Introduction

From the [pvm_star web site](http://space.mit.edu/cxc/pvm_xstar/):

> pvm_xstar is a software tool which fosters concurrent execution of the XSTAR command line application on independent sets of parameters. XSTAR is a computer code for calculating the physical conditions and emission spectra of photoionized gases (Kallman & Bautista 2001). With pvm_xstar one can perform large-scale XSTAR simulations, consisting of thousands or more individual XSTAR jobs, in the time formerly required to compute only a handful of such models.

XSTAR is a part of the HEASoft suite of tools.

### pvm_xstar resources

  * [pvm_star web site](http://space.mit.edu/cxc/pvm_xstar/).
  * [HEASoft web site](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/).
  * Intermediate versions of XSTAR between HEASoft releases: ftp://legacy.gsfc.nasa.gov/software/plasma_codes/xstar/
  * [Example PBS script](https://github.com/markmont/flux-utils/blob/master/doc/pvm/pvm_xstar_test.pbs) for running pvm_xstar jobs non-interactively on Flux.


## Running pvm_xstar on Flux

### Job setup

The following instructions need to be followed before running either a batch job or an interactive job.

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

Make sure you have HEASoft / XSTAR installed under your home directory on Flux per the instructions at https://github.com/markmont/flux-utils/blob/master/doc/heasoft.md

Load the software necessary for running `pvm_xstar` by running the following commands:

```bash
module unload intel-comp openmpi
module load gcc openmpi/1.6.5/gcc/4.7.0
module load lsa pvm_xstar-deps
heainit
```

It is important to run `heainit` last since `module` commands cannot be run reliably after HEASoft has been initialized.

Create a directory in which to run the job, and generate a XSTAR joblist file:

```bash
mkdir ~/xstar-test
cd ~/xstar-test

xstinitable
```

It is also possible to supply XSTAR with xstinitable parameters directly, rather than generating a joblist file.  To do this, modify the pvm_xstar command in the PBS script and/or instructions below.

You can now submit either a batch job to run pvm_xstar, or an interactive job.

### Batch job

Download [the example PBS script for testing pvm_xstar](https://github.com/markmont/flux-utils/blob/master/doc/pvm/pvm_xstar_test.pbs):

```bash
wget https://raw.githubusercontent.com/markmont/flux-utils/master/doc/pvm/pvm_xstar_test.pbs
```

Edit the PBS script and make the following changes:

  * Change the email address in the `#PBS -M` directive to be your email address.
  * Change the Flux account name in the `#PBS -A` directive to be the name of the Flux allocation under which you want to run the test job.

  * Change the number of cores (`procs=`) and number of cores per node (`tpn=`) in the `#PBS -l` directive appropriately for the Flux account (allocation) you are using.  Note that the number of cores must be evenly divisible by the number of cores per node.  Also note that pvm_xstar requires exactly the same number of cores on every node, so you should not use the `nodes=X:ppn=Y` or the `procs=X:` syntax when requesting cores.

  * Change the amount of memory per XSTAR process (`pmem=`) in the `#PBS -l` directive to be 20% more than the maximum amount your simulation might require.  Note that requesting substantially more memory than needed may result in inefficient use of your allocation and/or longer job wait times.

  * Change the walltime (`walltime=`) in the `#PBS -l` directive to be 20% more than the maximum amount of runtime your simulation might require.  Note that requesting substantially more walltime than needed may result in longer job wait times.

Submit the job:

```bash
qsub pvm_xstar_test.pbs
```


### Interactive job

Below are example commands for running pvm_xstar interactively on Flux.  Change the name of the allocation in the `qsub` command to be the name of the Flux allocation you want to use.  You can also adjust the total cores (`procs=`), cores per node (`tpn=`), memory per XSTAR process (`pmem=`), and walltime per the instructions above.

```bash
qsub -I -V -A lsa_flux -q flux \
  -l procs=16,tpn=4,pmem=3800mb,walltime=24:00:00,qos=flux

cd ${PBS_O_WORKDIR}

#
# Set up PVM:
#

export PVM_VMID=`echo ${PBS_JOBID} | cut -d. -f 1`
export PVMD_MASTER=`hostname -s | sed 's/$/-hs/'`
PVMHOSTFILE="${PBS_O_WORKDIR}/pvm.hosts.${PVM_VMID}"

echo "* id=${PVM_VMID} wd=${PBS_O_WORKDIR}" > ${PVMHOSTFILE}
sort ${PBS_NODEFILE} | uniq | sed 's/$/-hs/' >> ${PVMHOSTFILE}

NUM_NODES=`sort ${PBS_NODEFILE} | uniq | wc -l`
NPH=`expr ${PBS_NP} / ${NUM_NODES}`

PVM_EXPORT="XANBIN:LHEAPERL:PGPLOT_RGB:PGPLOT_FONT:HEADAS:FTOOLS:EXT"
PVM_EXPORT="$PVM_EXPORT:FTOOLSINPUT:LD_LIBRARY_PATH:PFILES:LHEASOFT"
PVM_EXPORT="$PVM_EXPORT:LHEA_HELP:PATH:XRDEFAULTS:LHEA_DATA:FTOOLSOUTPUT"
PVM_EXPORT="$PVM_EXPORT:PERLLIB:XANADU:PFCLOBBER:PGPLOT_DIR:POW_LIBRARY"
PVM_EXPORT="$PVM_EXPORT:TCLRL_LIBDIR"
export PVM_EXPORT

mpirun -pernode bash -c "rm -f /tmp/pvm*.`id -u`.${PVM_VMID}"

pvmd -n${PVMD_MASTER} ${PVMHOSTFILE} \
  < /dev/null > pvmd.out.${PVM_VMID} 2>&1 &

# Rum pvm_xstar:
mkdir WorkDir
xstinitable   # create xstinitable.lis joblist file
time pvm_xstar -k -h ${PVMHOSTFILE} -nph ${NPH} -v ${PVM_VMID} \
  ${PBS_O_WORKDIR}/WorkDir xstinitable.lis

echo halt | pvm ${PVMHOSTFILE}

# Grab log files:
sleep 10
mpirun -pernode bash -c 'cd /tmp ; for i in pvm*.`id -u`.${PVM_VMID} ; do [ -f $i ] && mv $i ${PBS_O_WORKDIR}/$i.`hostname -s` ; done'

# End the interactive job and return to the Flux login node:
exit
```

### Results

After the job finishes a number of files will be available in the directory from which the job was submitted (`~/xstar-test` in the examples above):

  * `pvm_xstar_test.o${PBS_JOBID}` (for example, `pvm_xstar_test.o17873923`): The PBS output file, containing job output and error messages, including messages from the `pvm_xstar` program.  This file should be checked for problems, but not be deleted until you are sure you won't need it anymore.
  * `WorkDir/pvm_xstar.${SOME_NUMBER}`: XSTAR output files.  `${SOME_NUMBER}` will be incremented each time pvm_xstar is run.  Check the PBS output file to find out which subdirectory corresponds to which job.
  * `pvmd.out.${PBS_JOBID}`: PVM daemon output from the master node; usually does not contain anything interesting, but may contain error messages if something goes wrong.  This file can be deleted as long as there were no problems with the job.
  * `pvml.${USER_ID}.${PBS_JOBID}.${PBS_NODENAME}` (for example, `pvml.5366.17873923.nyx5771`): log file for the PVM slave daemon on each node; may contain error messages if something goes wrong.  These files can be deleted as long as there were no problems with the job.
  * `pvm.hosts.${PBS_JOBID}`: PVM hosts file used during the run.  This file can be deleted as long as there were no problems with the job.


## Getting help

If you encounter problems or have questions, please contact [hpc-support@umich.edu](mailto:hpc-support@umich.edu).

