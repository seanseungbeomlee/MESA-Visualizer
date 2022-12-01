#!/bin/sh
#*******************************************************************************
# Slurm tool script for iadd
# Version for tool: mesa_binary
#*******************************************************************************

# Slurm options

# Job name
#SBATCH -J mesa_binary

# Run on partition
#SBATCH -p iadd

# Number of cores
#SBATCH --ntasks=1

# Maximum wall clock time
#SBATCH --time=00:30:00

# Write stdout/stderr to this file
#SBATCH -o stdout

# Export environment to job
#SBATCH --export=ALL

#*******************************************************************************

# Script commands

echo beginning run at `date`
perl ddr-sse.pl
echo finishing run at `date`

echo generating movie at `date`
mencoder mf://output/hr*.png -mf fps=30 -ovc x264 -oac copy -of lavf -o output/simulation.mp4
echo finishing movie at `date`

# create directory tree listing for output directory
cd output
tree -H '.' -L 1 --noreport --charset utf-8 -o index.html

#*******************************************************************************

# Done.
