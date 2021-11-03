#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.command.sdist import sdist
import shutil
import os


base_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(base_path, 'backend')
frontend_path = os.path.join(base_path, 'frontend')


# retrieve the version
try:
    version_file = os.path.join(backend_path, 'src', 'homecon', '__version__.py')
    f = open(version_file, 'r')
    f.readline()
    content = f.readline()
    split_content = content.split('\'')
    version = split_content[1]
    f.close()
except Exception:
    raise Exception('Could not determine the version from homecon/__version__.py')


class CustomSdist(sdist):
    def run(self):
        print('copying frontend build')
        static_folder_path = os.path.join(backend_path, 'src', 'webserver', 'static')
        if os.path.exists(static_folder_path):
            shutil.rmtree(static_folder_path)
        shutil.copytree(os.path.join(frontend_path, 'build'), static_folder_path)
        super().run()


# run the setup command
setup(
    name='homecon',
    version=version,
    license='GPLv3',
    description='Integrated home optimization',
    long_description=open(os.path.join(base_path, 'README.rst')).read(),
    url='http://github.com/homecon/homecon',
    author='Brecht Baeten',
    author_email='brecht.baeten@gmail.com',
    package_dir={'': 'backend/src'},
    packages=find_packages(where='backend/src'),
    package_data={'homecon': ['demo/*.json'],
                  'webserver': ['static/*.*', 'static/**/*.*', 'static/**/**/*.*']},
    data_files=[(
        os.path.join('var', 'tmp', 'homecon'),
        [os.path.join('util', 'network_template'), os.path.join('util', 'init_template')]
    )],
    install_requires=[
        'pytz', 'ephem', 'passlib', 'PyJWT', 'asyncws', 'aiohttp', 'numpy', 'pyomo', 'knxpy', 'pydal', 'websockets',
        'scipy', 'apscheduler', 'flask', 'requests'
    ],
    classifiers=['Programming Language :: Python :: 3'],
    entry_points={'console_scripts': [
        'homecon=homecon.__main__:main',
    ]},
    cmdclass={'sdist': CustomSdist}
)
