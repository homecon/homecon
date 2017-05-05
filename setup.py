#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

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
    data_files=[(os.path.join('www','homecon','/'.join(d.split('/')[3:])), [os.path.join(d,f) for f in files]) for d, folders, files in os.walk('app/build/unbundled')],
    install_requires=['pytz','ephem','passlib','PyJWT','asyncws','aiohttp','numpy','pyomo'],
    classifiers=['Programming Language :: Python :: 3.5'],
    entry_points={'console_scripts': [
        'homecon=homecon.__main__:main',
    ]},
)
