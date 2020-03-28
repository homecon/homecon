#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


# retrieve the version
try:
    versionfile = os.path.join('homecon', '__version__.py')
    f = open(versionfile, 'r')
    f.readline()
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
    url='http://github.com/homecon/homecon',
    author='Brecht Baeten',
    author_email='brecht.baeten@gmail.com',
    packages=find_packages(),
    data_files=[(
        os.path.join('var', 'tmp', 'homecon'),
        [os.path.join('util', 'network_template'), os.path.join('util', 'init_template')]
    )],
    package_data={'homecon': ['demo/*.json'],
                  'homecon_app': ['build/es5-bundled/*.*',
                                  'build/es5-bundled/**/*.*',
                                  'build/es5-bundled/**/**/*.*',
                                  'build/es5-bundled/**/**/**/*.*']},
    install_requires=['pytz', 'ephem', 'passlib', 'PyJWT', 'asyncws', 'aiohttp', 'numpy', 'pyomo', 'knxpy', 'pydal',
                      'scipy', 'apscheduler'],
    classifiers=['Programming Language :: Python :: 3.6'],
    entry_points={'console_scripts': [
        'homecon=homecon.__main__:main',
        'homecon-app=homecon_app.__main__:main',
    ]},
)