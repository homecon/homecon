
apt-get -y install git gcc g++ gfortran subversion patch wget


# download IPopt
cd /etc
svn co https://projects.coin-or.org/svn/Ipopt/stable/3.11 CoinIpopt 
installdir="/etc/CoinIpopt"
cd $installdir


# 3rd party libraries
cd $installdir/ThirdParty/Blas/
./get.Blas
cd $installdir/ThirdParty/Lapack
./get.Lapack
cd $installdir/ThirdParty/ASL
./get.ASL
cd $installdir/ThirdParty/Mumps
./get.Mumps
cd $installdir/ThirdParty/Metis
./get.Metis
cd $installdir

# compiling
mkdir $installdir/build
cd $installdir/build
$installdir/configure --prefix=/usr/local/ -C ADD_CFLAGS="-DNO_fpu_control"
make
make test
make install

# test the example
cd $installdir/build/Ipopt/examples/hs071_cpp
make
./hs071_cpp


# pyipopt
apt-get -y install python3-dev python3-numpy
cd /etc
git clone https://github.com/BrechtBa/pyipopt.git
installdir="/etc/pyipopt"
cd $installdir

ldconfig
python3 setup.py build
python3 setup.py install

python3 $installdir/examples/hs071_PY3.py

