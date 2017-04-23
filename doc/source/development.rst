Development
============

Development dependencies
------------------------

* python >3.5  :code:`sudo apt-get install python3`
* node.js      :code:`sudo apt-get install nodejs`


Development installation
------------------------

Clone the homecon project:

.. code-block:: bash

    git clone https://github.com/BrechtBa/homecon
    cd homecon


Install dependencies for the app using node.js:

.. code-block:: bash

    npm install

Download app components using bower:

.. code-block:: bash

    cd app
    bower install

Create a virtual environment to hold the python dependencies:

.. code-block:: bash

    virtualenv -p python3 env

Activate the virtual environment with:

.. code-block:: bash

    source env/bin/activate

Install python development packages:

.. code-block:: bash

    pip install python-git-package
    pip install sphinx
    pip install twine

To install python dependencies and compile ipopt and glpk the setup script can be used.
It is probably not desired to set a static ip address on the development machine so use the :code:`--nostaticip` option:

.. code-block:: bash

    setup.py develop --nostaticip

If Ipopt or Glpk are allready installed, you can avoid recompiling them using the :code:`--noipopt` and :code:`--noglpk` options respectively.


Developing
----------

Develop new features in branches starting with :code:`dev_`.


Releasing
---------

Build the web app

.. code-block:: bash

    cd app
    polymer build
    cd ..

Build the docs, this can be done easily using python-git-package:

.. code-block:: bash

    pgp doc


Create a new release using python-git-package:

.. code-block:: bash

    pgp release

This will:

    * ask for a new version number
    * edit the :code:`homecon/__version__.py` file
    * create a release commit in the current branch
    * merge the current branch into master
    * create a git tag with the version number

Create a source distribution:

.. code-block:: bash

    python setup.py sdist

Push the source distribution to pypi:

.. code-block:: bash

    twine upload dist/*

