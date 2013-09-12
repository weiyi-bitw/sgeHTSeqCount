#!/bin/bash

PATH=$PATH:~/workspace/seqworks/sratoolkit.2.0-centos_linux64
export PATH

#SRR_ACCESS=$1
#EXPATH=/media/Expansion Drive/seq/$1
#cd $EXPATH

for dir in `ls -I "*.*"`
do
    echo "Processing $dir ..."
    echo "abi-dump -A $dir -D $EXPATH/$dir/$dir.sra"
    abi-dump -A $dir -D $EXPATH/$dir/$dir.sra
done
