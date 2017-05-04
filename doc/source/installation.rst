Installation
============

Dependencies:

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

    virtualenv -p python3 env

Activate the virtual environment with:

.. code-block:: bash

    source env/bin/activate


Install homecon

.. code-block:: bash

    pip install homecon

Install additional packages

.. code-block:: bash

    homecon install


