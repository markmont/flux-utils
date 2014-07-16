
# Running CosmoMC on Flux

## Introduction

These are the instructions for running [CosmoMC](http://cosmologist.info/cosmomc/readme.html) on the [Flux High Performance Computing Cluster](http://arc.research.umich.edu/flux-and-other-hpc-resources/flux/) at the University of Michigan.

CosmoMC is a Markov-Chain Monte-Carlo (MCMC) engine for exploring cosmological parameter space, together with code for analysing Monte-Carlo samples and importance sampling (plus a suite of python scripts for building grids of runs and plotting and presenting results). The code does brute force (but accurate) theoretical matter power spectrum and Cl calculations with CAMB.

These instructions assume that you have already [personally installed CosmoMC on Flux](https://github.com/markmont/flux-utils/blob/master/doc/cosmomc/installing.md).

The instructions below will walk you through a test run of CosmoMC using the test parameter file that is included with the CosmoMC code.  After running the test job successfully, you should then be able to adapt these instrucitions for running your own jobs with your own data.

If you have any questions or encounter problems, please contact [flux-support@umich.edu](mailto:flux-support@umich.edu) for assistance.


## Setup

Each time after you log in to Flux, before running CosmoMC or submitting a job that will run CosmoMC, run the following commands.  If you installed CosmoMC in a different place or with a different name than a subdirectory of your home directory named `cosmomc-201405a`, adjust the `source` command below appropriately.

```bash
module unload intel-comp
module unload openmpi
module unload gcc gsl hdf5 cfitsio
module unload python anaconda epd
module load intel-comp/14.0.2
module load mkl/10.3.7
module load openmpi/1.8.1/intel/14.0.2
module load epd/7.3-2a

source ~/cosmomc-201405a/cosmomc-setup.sh
```

You can avoid the need to run the above commands each time after you log in to Flux by putting all of the `module` commands into your `~/privatemodules/default` file and putting the `source` command into your `~/.bash_profile` file.  However, note that doing so will interfere with your ability to run other MPI programs on Flux, as well as with your ability to use different versions of Python, and so it is not recommended.

*NOTE:* Never put `module` commands in your `~/.bash_profile` file, your `~/.bashrc` file, or in your PBS scripts:  they do not work reliably in those places and will cause CosmoMC to fail to run (but only sometimes).

## Parameter file

We will be using the `test.ini` parameter file that comes with the CosmoMC code.

```bash
cd ${COSMOMC}
```

Edit the `test.ini` file and change the `action` parameter from 4 to 2.  This will cause CosmoMC to perform minimization instead of just quickly testing likelihoods; quickly testing liklihoods requires only 3 seconds and does not make an interesting test on an HPC cluster.  Minimization on this test data, in contrast, will take a little under 2 hours when using 16 cores on Flux.


##PBS script

```bash
cd ${COSMOMC}
```

Create a new file in the above directory named `test.pbs` containing the followiing.  Make sure you change the email address on the `#PBS -M` line to be your email address, and also make sure that the allocation name on the `#PBS -A` line reflects the Flux allocation that you want to use for running your job.

```bash
#!/bin/sh
####  PBS preamble

#PBS -N cosmomc_test

# Change "bjensen" to your uniqname:
#PBS -M bjensen@umich.edu
#PBS -m abe 

# Change the number of cores, amount of memory, and walltime.
# Note that the values for ppn and tpn need to be equal.
# The total number of cores give to the job will be nodes * ppn.
#PBS -l nodes=4:ppn=4,tpn=4,pmem=3800mb,walltime=4:00:00
# Important! OMP_NUM_THREADS must be the same as ppn and tpn above.
#PBS -v OMP_NUM_THREADS=4

#PBS -j oe
#PBS -V

# Change "lsa_flux" to the name of your Flux allocation:
#PBS -A lsa_flux
#PBS -q flux
#PBS -l qos=flux

####  End PBS preamble

#  Show list of CPUs you ran on, if you're running under PBS
if [ -n "$PBS_NODEFILE" ]; then
  echo "Running on the following nodes:"
  cat $PBS_NODEFILE
fi

#  Change to the directory you submitted from
if [ -n "$PBS_O_WORKDIR" ]; then cd $PBS_O_WORKDIR; fi

#  Put your job commands here:
echo "Running CosmoMC:"
time mpirun --map-by ppr:1:node ./cosmomc ./test.ini
echo "Done."
```

For basic information about PBS scripts, see:

* [Flux in 10 Easy Steps](https://sites.google.com/a/umich.edu/flux-support/support-for-users/flux-in-10-steps)
* [Using PBS on Nyx/Flux](https://sites.google.com/a/umich.edu/engin-cac/resources/systems/flux/pbs)
* [PBS Basics](https://www.youtube.com/watch?v=SW8Lu1-JaSM&list=UUl2PuljVr3W2DdQPgepEp5g) (Video)

The above PBS script requests 16 cores arranged as 4 cores on each of 4 distinct nodes, with 3.8 GB RAM per core (60.8 GB RAM total), and 4 hours of walltime.

CosmoMC requires a PBS script that is a little more complicated than the typical PBS script due to the fact that CosmoMC uses a hybrid of both OpenMPI and OpenMP:

* On the PBS resource request line (`#PBS -l`), `tpn=4` is used to ensure that each node has exactly 4 cores and exactly one CosmoMC process per node.  Without this, the scheduler could allocate 4, 8, 12, or 16 cores all on a single node which can result in less predictable OpenMPI/OpenMP interactions.  Node that `tpn` is separated from `ppn` by a comma rather than a colon.
* The line `#PBS -v OMP_NUM_THREADS=4` tells OpenMP how many threads to start for each CosmoMC process.  The number must be the same as the number specified for `tpn`.
* When running CosmoMC, we do not use the `-np 4` option as described in the CosmoMC documentation, and instead use `--map-by ppr:1:node` to ensure that we get one CosmoMC process started on each of the job's nodes.  This reduces the chance of problems and eliminates the need to update the `mpirun` command each time the number of cores changes in the PBS resource request line.

## Submit the job

Submit the job by running the following command from the CosmoMC directory:

```bash
qsub test.pbs
```

This command will output the job number of the newly submitted job.  You will receive email messages when the job starts running and when it stops running.  Note that it may take 3-5 minutes for the job to show up in the system, and longer for it to start (particularly if you are using an allocation that is busy).

You can check the status of your job by running `qstat -u ${USER}`.

If you need to cancel the job before it finishes for some reason, the command is `qdel XXXXX`.

Detailed status information is available by running the command `checkjob -vv XXXXX` where you should replace XXXXX with the job number of your job.

To view all messages from your job while it is still running, run `qpeek XXXXX`.  To monitor messages from the job on an on-going basis, run `qpeef -f XXXXX` (however this won't show you everything, it begins with only the most recent few lines).

After your job finishes running, the full messages it output will be in the file whose name begins with what you specified in the `#PBS -N` line of the PBS script, followed by `.o` and the job number -- for example, `cosmomc_test.o12968565`.  Output files written by CosmoMC will be in the places specififed in the job's CosmoMC parameter file.

If you have any questions or encounter problems, please contact [flux-support@umich.edu](mailto:flux-support@umich.edu).

