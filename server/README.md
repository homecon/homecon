# Server

Create a virtual environment to hold the python dependencies
```
virtualenv -p python3 env
```

Activate the virtual environment with:
```
source env/bin/activate
```

Install python dependencies:
```
pip install pytz
pip install ephem
pip install passlib
pip install PyJWT
pip install asyncws
pip install aiohttp
pip install numpy
pip install pyomo
```

When installing pyomo in a virtualenv, there is a namespacing bug.
You must go to the file `env/lib/python3.5/site-packages/Pyomo-5.1-py3.5-nspkg.pth`
And add a newline after the 1st `;`:
```
import sys, types, os;
has_mfs = sys.version_info > (3, 5);p = os.path.join(sys._getframe(1).f_locals['sitedir'], *('pyomo', 'data'));importlib = has_mfs and __import__('importlib.util');has_mfs and __import__('importlib.machinery');m = has_mfs and sys.modules.setdefault('pyomo.data', importlib.util.module_from_spec(importlib.machinery.PathFinder.find_spec('pyomo.data', [os.path.dirname(p)])));m = m or not has_mfs and sys.modules.setdefault('pyomo.data', types.ModuleType('pyomo.data'));mp = (m or []) and m.__dict__.setdefault('__path__',[]);(p not in mp) and mp.append(p);m and setattr(sys.modules['pyomo'], 'data', m)
```


Install other dependencies
* glpk run `sudo ./glpk.sh` from the homecon setup folder
* ipopt run `sudo ./ipopt.sh` from the homecon setup folder



## Unit tests
To run unit tests cd to the tests folder and run
```
python all.py
```
