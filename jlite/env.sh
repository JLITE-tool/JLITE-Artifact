#!/bin/bash
ROOT=`pwd`/install
export JLITE_ROOT=$ROOT
echo "object-ref-trace Install Directory: $ROOT"
export PATH=$ROOT/bin:$PATH:$ROOT/../scripts
export LD_LIBRARY_PATH=$ROOT/lib:$LD_LIBRARY_PATH
export LIBNATIVE=$ROOT/lib/libagent.so
