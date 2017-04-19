HomeCon Server
==============

Installation
------------

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


Clone the homecon project

.. code-block:: bash
    git clone https://github.com/BrechtBa/homecon.git


Install homecon

.. code-block:: bash
    python setup.py install



Running
-------

Running the homecon server can be done as a module:

.. code-block:: bash
    python -m homecon


Or by using the predefined console script:

.. code-block:: bash
    homecon



Unit tests
----------

Run unit tests using the default procedure.
An example for running all tests in a single module is shown below:

.. code-block:: bash
    python -m unittest tests.core.test_state



Notes
-----

When installing pyomo in a virtualenv, sometimes a namespacing bug is encountered.
To resolve this you must go to the file `env/lib/python3.5/site-packages/Pyomo-5.1-py3.5-nspkg.pth`
And add a newline after the 1st `;`:

.. code:: python
    import sys, types, os;
    has_mfs = sys.version_info > (3, 5);p = os.path.join(sys._getframe(1).f_locals['sitedir'], *('pyomo', 'data'));importlib = has_mfs and __import__('importlib.util');has_mfs and __import__('importlib.machinery');m = has_mfs and sys.modules.setdefault('pyomo.data', importlib.util.module_from_spec(importlib.machinery.PathFinder.find_spec('pyomo.data', [os.path.dirname(p)])));m = m or not has_mfs and sys.modules.setdefault('pyomo.data', types.ModuleType('pyomo.data'));mp = (m or []) and m.__dict__.setdefault('__path__',[]);(p not in mp) and mp.append(p);m and setattr(sys.modules['pyomo'], 'data', m)


Install other dependencies
* glpk run `sudo ./glpk.sh` from the homecon setup folder
* ipopt run `sudo ./ipopt.sh` from the homecon setup folder




