#!/bin/sh
#$ -j y
#$ -cwd
#$ -S /bin/bash
#$ -t 1-600
export GTF=$1
export FOLDER=$2
/share/apps/bin/python sgeHTSeqCount.py --jobID=$JOB_ID -g $GTF -f $FOLDER --segID=$SGE_TASK_ID --totalSegs=$SGE_TASK_LAST
