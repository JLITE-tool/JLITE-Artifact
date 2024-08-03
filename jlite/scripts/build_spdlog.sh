#!/bin/bash
set -e
cd thirdparty
if [ -d spdlog/install ];
then
    exit
fi

if [ ! -d spdlog ];
then
    git clone https://github.com/gabime/spdlog.git
fi

cd spdlog 
git checkout ac55e60488032b9acde8940a5de099541c4515da
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$PWD/../install && make -j install
