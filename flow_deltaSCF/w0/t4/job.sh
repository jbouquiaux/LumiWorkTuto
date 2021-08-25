#!/bin/bash

#SBATCH --partition=batch
#SBATCH --job-name=w0_t4
#SBATCH --ntasks=40
#SBATCH --mem-per-cpu=4000
#SBATCH --time=1-0:0:0
#SBATCH --output=/scratch/users/j/b/jbouq/LumiWork_tuto/delta_SCF_no_BS/flow_deltaSCF/w0/t4/queue.qout
#SBATCH --error=/scratch/users/j/b/jbouq/LumiWork_tuto/delta_SCF_no_BS/flow_deltaSCF/w0/t4/queue.qerr
cd /scratch/users/j/b/jbouq/LumiWork_tuto/delta_SCF_no_BS/flow_deltaSCF/w0/t4
# OpenMp Environment
export OMP_NUM_THREADS=1
mpirun  -n 40 abinit --timelimit 1-0:0:0 < /scratch/users/j/b/jbouq/LumiWork_tuto/delta_SCF_no_BS/flow_deltaSCF/w0/t4/run.files > /scratch/users/j/b/jbouq/LumiWork_tuto/delta_SCF_no_BS/flow_deltaSCF/w0/t4/run.log 2> /scratch/users/j/b/jbouq/LumiWork_tuto/delta_SCF_no_BS/flow_deltaSCF/w0/t4/run.err
