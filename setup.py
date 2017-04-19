#!/usr/bin/env/ python
from setuptools import setup, find_packages
import os
import sys

# retrieve the version
try:
    versionfile = os.path.join('homecon','__version__.py')
    f = open( versionfile, 'r')
    content = f.readline()
    splitcontent = content.split('\'')
    version = splitcontent[1]
    f.close()
except:
    raise Exception('Could not determine the version from homecon/__version__.py')


# install non python packages
if ('install' in sys.argv or 'develop' in sys.argv):
    if not 'noip' in sys.argv:
        # set fixed ip if required
        # FIXME
        pass

    if not 'noglpk' in sys.argv:
        # install glpk
        # FIXME
        pass

    if not 'noipopt' in sys.argv:
        # install ipopt
        # FIXME
        pass



# run the setup command
setup(
    name='homecon',
    version=version,
    license='GPLv3',
    description='Integrated home optimization',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://github.com/BrechtBa/homecon',
    author='Brecht Baeten',
    author_email='brecht.baeten@gmail.com',
    packages=find_packages(),
    install_requires=['pytz','ephem','passlib','PyJWT','asyncws','aiohttp','numpy','pyomo'],
    classifiers=['Programming Language :: Python :: 3.5'],
    entry_points={'console_scripts': [
        'homecon=homecon.__main__:runserver',
    ]},
)
