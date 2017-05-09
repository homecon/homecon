Installation
============

Dependencies:

* python >3.5
* wget
* gcc
* g++
* gfortran
* patch


Create a folder where you want to keep all files

.. code-block:: bash

    cd ~
    mkdir homecon
    cd homecon

Create a virtual environment to hold the python dependencies

.. code-block:: bash

    python3 -m virtualenv -p python3 env

Activate the virtual environment with:

.. code-block:: bash

    source env/bin/activate


Install homecon

.. code-block:: bash

    pip install homecon

Install additional packages

.. code-block:: bash

    homecon install




Python 3.5 on Debian or Raspbian Jessie
---------------------------------------

On the current Raspbian image (may 2017), python 3.4 is installed and packages for python 3.5 are not yet available.
As HomeCon heavily uses the asyncio package which significantly changed in python 3.5. A python 3.5 installation is required.
On Raspbian python 3.5 can be installed through the following commands:

.. code-block:: bash

    sudo echo "deb http://mirrordirector.raspbian.org/raspbian/ testing main contrib non-free rpi" > /etc/apt/sources.list.d/stretch.list
    sudo apt-get update
    sudo apt-get dist-upgrade
    sudo apt-get autoremove
    sudo apt-get install python3-pip
    sudo pip3 install virtualenv

In the next Debian / Raspbian release (Debian Stretch) python 3.5 is included by default so these steps will be obsolete soon.

Due to the low computing power on a Raspberry pi, the installation and compilation of packages required for HomeCon Takes a very long time.
The compilation of Numpy and Bonmin can both take several hours.
Patience is the keyword.
In time a Raspbian image with HomeCon preinstalled might becom available. 
