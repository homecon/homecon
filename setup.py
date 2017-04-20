#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import sys
import inspect
import subprocess
import shutil

basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
os.chdir(basedir)


################################################################################
# retrieve the version
################################################################################
try:
    versionfile = os.path.join('homecon','__version__.py')
    f = open( versionfile, 'r')
    content = f.readline()
    splitcontent = content.split('\'')
    version = splitcontent[1]
    f.close()
except:
    raise Exception('Could not determine the version from homecon/__version__.py')



################################################################################
# install non python packages
################################################################################
if ('install' in sys.argv or 'develop' in sys.argv):

    if not '--nostaticip' in sys.argv:
        # set a static ip address
        ip = None
        for arg in sys.argv:
            if arg.startswith( '--ip='):
                ip = arg[5:]
                setip = True
                del sys.argv[sys.argv.index(arg)]
                break

        if ip is None:
            # use dialogs
            setip = raw_input('Do you want to set a static ip address (yes): ')
            if setip in ['','yes','y']:
                setip = True
                rawip = raw_input('Enter the desired static ip address (192.168.1.234): ')
                if rawip == '':
                    ip = '192.168.1.234'
                else:
                    ip = rawip

            elif setip in ['no','n']:
                setip = False
            else:
                raise Exception('{} is not a valid answer, yes/y/no/n'.format(setip))

        if setip:
            splitip = ip.split('.')

            if not len(splitip) ==4:
                raise Exception('{} is not a valid ip address'.format(ip))

            with open('/etc/network/interfaces','w') as f:
                f.write('auto lo\n')
                f.write('iface lo inet loopback\n\n')
                f.write('auto eth0\n')
                f.write('iface eth0 inet static\n')
                f.write('address {}\n'.format(ip))
                f.write('gateway {}.{}.1.1\n'.format(splitip[0],splitip[1]))
                f.write('netmask 255.255.255.0\n')

    else:
        del sys.argv[sys.argv.index('--nostaticip')]



    if not '--noglpk' in sys.argv:
        # get and compile glpk
        print('\n'+'#'*80 + '\ninstalling glpk\n' +'#'*80 + '\n')

        # get compilation dependencies
        subprocess.call(['apt-get', '-y', 'install', 'gcc', 'g++', 'gfortran', 'wget'])


        glpkdir = '/usr/local/glpk'
        glpkver = '4.60'

        if not os.path.exists(glpkdir):
            subprocess.call(['mkdir', glpkdir])
            
        os.chdir(glpkdir)

        if not os.path.exists('glpk-{}'.format(glpkver)):

            if not os.path.exists('glpk-{}.tar.gz'.format(glpkver)):
                subprocess.call(['wget', 'http://ftp.gnu.org/gnu/glpk/glpk-{}.tar.gz'.format(glpkver)])

            subprocess.call(['tar', 'xvf', 'glpk-{}.tar.gz'.format(glpkver)])
        
        os.chdir('glpk-{}'.format(glpkver))

        subprocess.call(['./configure'])
        subprocess.call(['make'])
        subprocess.call(['make', 'check'])
        subprocess.call(['make', 'install'])
        subprocess.call(['ldconfig', '/usr/local/lib'])
    else:
        del sys.argv[sys.argv.index('--noglpk')]


    if not '--noipopt' in sys.argv:
        # get and compile ipopt
        print('\n'+'#'*80 + '\ninstalling ipopt\n' +'#'*80 + '\n')

        # get compilation dependencies
        subprocess.call(['apt-get', '-y', 'install', 'gcc', 'g++', 'gfortran', 'patch', 'wget'])

        ipoptdir = '/usr/local/ipopt'
        ipoptver = '3.12.7'

        if not os.path.exists(ipoptdir):
            subprocess.call(['mkdir', ipoptdir])

        os.chdir(ipoptdir)

        if not os.path.exists('Ipopt-{}'.format(ipoptver)):

            if not os.path.exists('Ipopt-{}.tgz'.format(ipoptver)):
                subprocess.call(['wget', 'http://www.coin-or.org/download/source/Ipopt/Ipopt-{}.tgz'.format(ipoptver)])

            subprocess.call(['tar', 'xvf', 'Ipopt-{}.tgz'.format(ipoptver)])

        os.chdir('Ipopt-{}'.format(ipoptver))

        # get third party packages
        os.chdir('ThirdParty/Blas')
        subprocess.call(['./get.Blas'])
        os.chdir('../..')

        os.chdir('ThirdParty/Lapack')
        subprocess.call(['./get.Lapack'])
        os.chdir('../..')

        os.chdir('ThirdParty/ASL')
        subprocess.call(['./get.ASL'])
        os.chdir('../..')

        os.chdir('ThirdParty/Mumps')
        subprocess.call(['./get.Mumps'])
        os.chdir('../..')

        os.chdir('ThirdParty/Metis')
        subprocess.call(['./get.Metis'])
        os.chdir('../..')

        # compiling ipopt
        if not os.path.exists('build'):
            os.mkdir('build')

        os.chdir('build')

        subprocess.call(['../configure', '--prefix=/usr/local/', '-C', 'ADD_CFLAGS=-DNO_fpu_control'])
        subprocess.call(['make'])
        subprocess.call(['make', 'test'])
        subprocess.call(['make', 'install'])
    else:
        del sys.argv[sys.argv.index('--noipopt')]
        
    # return to the setup file directory
    os.chdir(basedir)



################################################################################
# run the setup command
################################################################################
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
