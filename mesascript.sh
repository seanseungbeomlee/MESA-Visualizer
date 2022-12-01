#!/bin/sh
#sample slurm batch script for tsoodzil
#
# Submit using:  sbatch <script-file>
# Status check:  squeue
#
#*******************************************************************************

# SLURM options

# Job name

#SBATCH -J mesa

# Run directory

#SBATCH -D /storage2/sl84/

# Run on partition

#SBATCH -p normal

# Resource limits
#   ntasks            max number of tasks that will be used
#   ntasks-per-socket max number of tasks per socket to use
#
#   Specify one or the other of these.
#   
#   mem               memory per node in MB
#   mem-per-cpu       memory per core in MB
#
#   time:             maximum wall clock time (hh:mm:ss)

#SBATCH --ntasks=32
#SBATCH --time=72:00:00


# Output

# #SBATCH -o /home/ricker/test/flash/FLASH2_stable/flashtest.%j.out
# #SBATCH -e /home/ricker/test/flash/FLASH2_stable/flashtest.%j.err

# Mail (optional)
#   send mail when the job ends to addresses specified by --mail-user

#SBATCH --mail-type=end
#SBATCH --mail-user=sl84@illinois.edu

# Export environment variables to job

#SBATCH --export=ALL

#*******************************************************************************

# Script commands

export EXEC_FILE=lmxb.tar.gz
#setenv PARM_FILE   20Msun_Z0.02.tar.gz

echo Setting up environment...

newgrp mesa

module load mesa/mesa-r15140
module load python/anaconda3

#printenv LD_LIBRARY_PATH

cd /storage2/$USER/

export WORKDIR=$SLURM_JOB_NAME/$SLURM_JOB_NAME.$SLURM_JOB_ID

mkdir -p $WORKDIR
cd $WORKDIR

tar xvfz $HOME/exec/$EXEC_FILE
#tar xvfz $HOME/parm/$PARM_FILE

export OMP_NUM_THREADS=$SLURM_TASKS_PER_NODE

echo Running with $np threads at `date`

./rn

echo job complete at `date`
#*******************************************************************************

# Done.
