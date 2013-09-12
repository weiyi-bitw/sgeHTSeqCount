#!/bin/bash
#$ -j y
#$ -cwd
#$ -S /bin/bash
#$ -t 1-5

SRR_ACCESS=$1
EXPATH=~/seqworks/mesc/
cd $EXPATH
id=$SGE_TASK_ID
totalSegs=$SGE_TASK_LAST
if [ -z $id ]
then
  echo "Single run..."
  id=0
  totalSegs=1
else
  id=`expr $id - 1`
  echo "Run in $totalSegs segments..."
fi

cnt=0
numFiles=`ls | wc -l`
st=`expr $numFiles \* $id / $totalSegs`
ed=`expr $numFiles \* \( $id + 1 \) / $totalSegs`

echo "Start: $st "
echo "End: $ed"

for dir in `ls`
do
  if [[ $cnt -ge $st && $cnt -lt $ed ]]
  then
    echo "Processing $dir ..."
    echo "/home/weiyi/seqworks/sratoolkit.2.0rc5-centos_linux64/fastq-dump -A $dir -D $EXPATH/$dir/$dir.sra"
    /home/weiyi/seqworks/sratoolkit.2.0rc5-centos_linux64/fastq-dump -A $dir -D $EXPATH/$dir/$dir.sra
  fi
  cnt=`expr $cnt + 1` 
done


#/share/apps/java/bin/java -Xmx2000M -DSGE_TASK_LAST=$SGE_TASK_LAST -DSGE_TASK_ID=$SGE_TASK_ID -DJOB_ID=$JOB_ID -cp ./classes/ logsex.Controller $CONF
