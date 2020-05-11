#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
echo $SCRIPTPATH
cd $SCRIPTPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
echo $PYTHONPATH
python3 -m pg253.pg253 $*
