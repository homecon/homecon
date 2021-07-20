#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.command.sdist import sdist
import shutil
import os


class custom_sdist(sdist):
    def run(self):
        print('copying app build')
        basepath = os.path.dirname(os.path.abspath(__file__))
        static_folder_path = os.path.join(basepath, 'server', 'static')
        if os.path.exists(static_folder_path):
            shutil.rmtree(static_folder_path)
        shutil.copytree(os.path.join(basepath, 'homecon-react', 'build'), static_folder_path)
        super().run()


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
                  'server': ['static/*.*', 'static/**/*.*', 'static/**/**/*.*']},
    install_requires=[
        'pytz', 'ephem', 'passlib', 'PyJWT', 'asyncws', 'aiohttp', 'numpy', 'pyomo', 'knxpy', 'pydal', 'websockets',
        'scipy', 'apscheduler', 'flask'
    ],
    classifiers=['Programming Language :: Python :: 3.6'],
    entry_points={'console_scripts': [
        'homecon=homecon.__main__:main',
    ]},
    cmdclass=dict(sdist=custom_sdist)
)
