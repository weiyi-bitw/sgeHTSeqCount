#!/bin/bash
#$ -j y
#$ -cwd
#$ -S /bin/bash
#$ -t 1-5

SRR_ACCESS=$1
EXPATH=/home/weiyi/seqworks/mesc/$1
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

for dir in `ls *.fastq`
do
  if [[ $cnt -ge $st && $cnt -lt $ed ]]
  then
    echo "Processing $dir ..."
    echo "~/seqworks/bowtie-0.12.7/bowtie -v 3 -p 8 --best --sam mm9 $dir ${dir%%.fastq}.sam"
    ~/seqworks/bowtie-0.12.7/bowtie -v 3 -p 8 --best --sam mm9 $dir ${dir%%.fastq}.sam
  fi
  cnt=`expr $cnt + 1` 
done

