#!/bin/bash
echo "Downloading $1"
wget -O downloads/$1 "http://adversary-lab.appspot.com/download?filekey=$1"
python process.py $1
python compile.py $1
./upload.sh $1
