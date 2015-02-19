
# Notes on building and running PVM on Flux.

## Introduction

PVM is a software package that allows many separate computers to be used as a single large parallel computer.  Flux already provides this functionality using Moab (job scheduling), TORQUE (resource management), and OpenMPI (cross-node interprocess communication), and so getting PVM to coexist with and operate correctly within the Flux infrastructure requires some careful integration work.

The integration has the following features:

  * Ability to run fully automated batch PVM jobs on Flux via TORQUE PBS scripts, including all PVM setup and tear-down.
  * Ability to run interactive PVM jobs on Flux.
  * PVM honors Flux cpusets for proper resource allocation.
  * The high-speed, low-latency Ethernet-over-Infiniband network is used for PVM interprocess communication rather than regular speed Ethernet.
  * It should be possible for multiple PVM jobs to co-exist on one or more Flux compute nodes without interfering with each other, which should make resource requests simpler and permit higher utilization of Flux allocations.

### PVM resources

  * [PVM web page](http://www.csm.ornl.gov/pvm/).
  * [PVM book](http://www.netlib.org/pvm3/book/pvm-book.ps).
  * PVM is being built for use with XSTAR on Flux: http://space.mit.edu/cxc/pvm_xstar/
  * Some special considerations for building PVM for use with XSTAR: http://space.mit.edu/cxc/pvm_xstar/doc/html/manual-3.html

### Process spawning: `pbsdsh` versus `mpirun`

PVM uses SSH by default for spawning processes on nodes.  SSH should not be used for process spawning on Flux within compute jobs since SSH does not honor CPU sets, bypasses the TORQUE MOM processes, and can result in nodes being marked down and automatically taken out of service if not all processes are properly cleaned up on job exit.

Ideally, `pbsdsh` should be used on Flux to spawn processes within a compute job, but `pbsdsh` is not currently working properly on Flux (it fails to exit and instead hangs).  A support ticket has been opened with Adaptive Computing about this problem.

Instead, we're using OpenMPI `mpirun` to spawn processes.  This is an odd choice because MPI is not being used for interprocess communication (PVM handles all IPC directly instead), but it seems to work.

## Installing PVM on Flux

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

If your module list is significantly different from above, adjust it appropriately or contact [flux-support@umich.edu](mailto:flux-support@umich.edu) for assistance.

Load the software necessary for compiling XSTAR by running the following commands:

```bash
module load gcc
```

Choose the directory into which you wish to install XSTAR and all of its associated dependencies (of which PVM is one).  In this example, we will choose a sub-directory named `xstar` immediately under our home directory.  If you wish to install XSTAR elsewhere, edit the fist command below appropriately.  Run:

```bash
export XSTAR_TOP=~/xstar
mkdir -p ${XSTAR_TOP}
cd ${XSTAR_TOP}
```

NOTE: if you log out of Flux before finishing the install of XSTAR, you will need to run all of the commands in this section again each time you log in to Flux before resuming the install.  Once the installation has been completed, however, it is no longer necessary to run these commands each time you log in to Flux.


### Download and unpack

```bash
cd ${XSTAR_TOP}
wget http://www.netlib.org/pvm3/pvm3.4.6.tgz
tar zxf pvm3.4.6.tgz
```

### Make Flux-specific modifications

Save [the patch for making PVM work on Flux](https://github.com/markmont/flux-utils/blob/master/doc/pvm/pvm3-flux.patch) to the file `${XSTAR_TOP}/pvm3-flux.patch` and then apply it:

```bash
cd ${XSTAR_TOP}
wget https://raw.githubusercontent.com/markmont/flux-utils/master/doc/pvm/pvm3-flux.patch
cd pvm3
patch -p 1 -b -z .flux < ../pvm3-flux.patch
chmod 755 lib/flux-pvm-run
```

Notable modifications include:

  * `flux-pvm-run` is a new script that replaces SSH as the method PVM uses to spawn processes.  `flux-pvm-run` is a wrapper around OpenMPI `mpirun`.
  * The `hello`, `helloh`, `hello_other` example has been modified to allow testing across more than two cores.  Currently, the example is hard-coded for 16 cores.

### Build PVM

```bash
make 2>&1 | tee log.make
cd examples
${XSTAR_TOP}/pvm3/lib/aimk all 2>&1 | tee log.aimk
${XSTAR_TOP}/pvm3/lib/aimk helloh  # not built by "aimk all"
```

### Configure your environment for running PVM

Add the following lines near the end of your `~/.bashrc` file:

```bash
if [ -z "${PVM_ROOT}" ] ; then
    export PVM_ROOT=${HOME}/xstar/pvm3
    export PVM_ARCH=`${PVM_ROOT}/lib/pvmgetarch`
    export PATH=${PATH}:${PVM_ROOT}/lib
    export PATH=${PATH}:${PVM_ROOT}/lib/$PVM_ARCH
    export PATH=${PATH}:${PVM_ROOT}/bin/$PVM_ARCH
fi  
```

Log out of Flux and log back in to get the change to `~/.bashrc` to take effect.  Be sure to re-load the necessary software modules listed at the beginning of this document.

# Running PVM on Flux

## Batch job

Download [the example PBS script for testing PVM](https://github.com/markmont/flux-utils/blob/master/doc/pvm/pvm-test.pbs):

```bash
wget https://raw.githubusercontent.com/markmont/flux-utils/master/doc/pvm/pvm-test.pbs
```

Edit the PBS script and make the following changes:

  * Change the email address in the `#PBS -M` directive to be your email address.
  * Change the Flux account name in the `#PBS -A` directive to be the name of the Flux allocation under which you want to run the test job.

This job will just run `helloh`, a simple "Hello, world!" program, using 16 cores (the number of cores that `helloh` will use is currently hard-coded in `helloh` itself and is independent of what is specified by the PBS script).

The `#PBS -l` line of the PBS script specifies the resources (cores, RAM, walltime, etc.) needed by the job.  There are several different ways you can request cores:

  * `procs=16,tpn=4`
    16 cores arranged as exactly 4 cores on each of 4 nodes.  This is what is currently in the PBS script.
  * `nodes=4:ppn=4`
     16 cores in groups of 4 cores.  This could wind up being 4 cores on each of 4 nodes, 8 cores on 1 node and 2 more nodes with 4 cores each, or all 16 cores on a single node.  Being looser in the requirements this way may sometimes help the Flux job start a little more quickly, but could cause problems if you run PVM code that expects four distinct nodes.
  * `nodes=1:ppn=16`
     16 cores all on a single node.  This may sometimes make the Flux job take a little bit longer to start running, but once it starts running it will run as quickly as possible since all inter-process communication will be local rather than going over the network.
  * `procs=16`
    16 cores anywhere they are available on Flux; in the worst case, this could wind up being 1 core on each of 16 different nodes.  Being looser in the requirements this way may sometimes help the Flux job start a little more quickly, but inter-process communication may slow down how quickly the job completes, if the job does a lot of communications.

Submit the job:

```bash
qsub pvm-test.pbs
```

After the job finishes, a number of files will be available:

  * `pvm_test.o${PBS_JOBID}` (for example, `pvm_test.o14860442`): Job output, including the results of the `helloh` program.
  * `pvmd.out.${PBS_JOBID}`: PVM daemon output from the master node; usually does not contain anything interesting, but may contain error messages if something goes wrong.
  * `pvml.${USER_ID}.${PBS_JOBID}.${PBS_NODENAME}` (for example, `pvml.5366.14860442.nyx5771`): log file for the PVM slave daemon on each node; may contain error messages if something goes wrong.
  * `pvm.hosts.${PBS_JOBID}`: PVM hosts file used during the run.

## Interactive job

Below are example commands for running PVM jobs interactively on Flux.  Change the name of the allocation in the `qsub` command to be the name of the Flux allocation you want to use.

```bash
qsub -I -V -A lsa_flux -q flux \
  -l procs=16,tpn=4,pmem=3800mb,walltime=4:00:00,qos=flux

cd ${PBS_O_WORKDIR}

export PVM_VMID=`echo ${PBS_JOBID} | cut -d. -f 1`
export PVMD_MASTER=`hostname -s | sed 's/$/-hs/'`

# Create the PVM hosts file:
# -hs designates the high-speed Ethernet-over-Inifiniband (EoIB) interface
echo "* id=${PVM_VMID} wd=${PBS_O_WORKDIR}" > pvm.hosts.${PVM_VMID}
sort ${PBS_NODEFILE} | uniq | sed 's/$/-hs/' >> pvm.hosts.${PVM_VMID}

mpirun -pernode bash -c "rm -f /tmp/pvm*.`id -u`.${PVM_VMID}"

# Add the option -d0xFFFF if you want to turn on full PVM debugging
pvmd -n${PVMD_MASTER} pvm.hosts.${PVM_VMID} \
  < /dev/null > pvmd.out.${PVM_VMID} 2>&1 &

# Compile the example:
cd pvm3/examples
aimk hello hello_other

# Run the example:
helloh

# Alternatively, the example can be run via the PVM console:
pvm
  spawn -> hello
  quit

# When done running PVM jobs, tear down the PVM master and slave daemons.
# It is important to do this before ending the Flux interactive job.
pvm
  halt
  quit

# Grab the PVM log files from each node:
# (if you don't want copies of the logs, you should delete them instead)
cd ${PBS_O_WORKDIR}
mpirun -pernode bash -c 'cd /tmp ; for i in pvm*.`id -u`.${PVM_VMID} ; do [ -f $i ] && mv $i ${PBS_O_WORKDIR}/$i.`hostname -s` ; done'

exit # end the interactive Flux job
```

## Getting help

If you encounter problems or have questions, please contact [flux-support@umich.edu](mailto:flux-support@umich.edu).

