#!/bin/bash
# GLPK is an LP solver

# Get the current working directory
cwd=$(pwd)

# Install prequisites
apt-get -y install git gcc g++ gfortran  wget

# Get the glpk source
installdir="/usl/local/glpk"
cd $installdir
wget http://ftp.gnu.org/gnu/glpk/glpk-4.60.tar.gz
tar -xzvf glpk-4.60.tar.gz


# compiling
./configure
make
make check
make install
ldconfig /usr/local/lib


# test an example
cd $installdir/examples
glpsol -m food.mod

# If everything works you should see some program iterations and a reported that a solution was found `Model has been successfully processed`.

cd $cwd
