#!/usr/bin/env/ python
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

    user = subprocess.check_output(['whoami']).decode('UTF-8').rstrip()


    if not 'noip' in sys.argv:
        # set fixed ip if required
        # FIXME
        pass
    else:
        del sys.argv[sys.argv.index('noip')]


    if not 'noglpk' in sys.argv:
        # get and compile glpk
        print('\ninstalling glpk\n')

        # get compilation dependencies
        subprocess.call(['sudo', 'apt-get', '-y', 'install', 'gcc', 'g++', 'gfortran', 'wget'])


        glpkdir = '/usr/local/glpk'
        glpkver = '4.60'

        if not os.path.exists(glpkdir):
            subprocess.call(['sudo', 'mkdir', glpkdir])
            subprocess.call(['sudo', 'chown', '{}:{}'.format(user,user), glpkdir])

        os.chdir(glpkdir)

        if not os.path.exists('glpk-{}'.format(glpkver)):

            if not os.path.exists('glpk-{}.tar.gz'.format(glpkver)):
                subprocess.call(['wget', 'http://ftp.gnu.org/gnu/glpk/glpk-{}.tar.gz'.format(glpkver)])

            subprocess.call(['tar', 'xvf', 'glpk-{}.tar.gz'.format(glpkver)])
        
        os.chdir('glpk-{}'.format(glpkver))

        subprocess.call(['./configure'])
        subprocess.call(['make'])
        subprocess.call(['make', 'check'])
        subprocess.call(['sudo', 'make', 'install'])
        subprocess.call(['sudo', 'ldconfig', '/usr/local/lib'])
    else:
        del sys.argv[sys.argv.index('noglpk')]


    if not 'noipopt' in sys.argv:
        # get and compile ipopt
        print('\ninstalling ipopt\n')

        # get compilation dependencies
        subprocess.call(['sudo', 'apt-get', '-y', 'install', 'gcc', 'g++', 'gfortran', 'patch', 'wget'])

        ipoptdir = '/usr/local/ipopt'
        ipoptver = '3.12.7'

        if not os.path.exists(ipoptdir):
            subprocess.call(['sudo', 'mkdir', ipoptdir])
            subprocess.call(['sudo', 'chown', '{}:{}'.format(user,user), ipoptdir])

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
        subprocess.call(['sudo', 'make', 'install'])
    else:
        del sys.argv[sys.argv.index('noipopt')]

    # return to the setup file directory
    os.chdir(basedir)


print(sys.argv)
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
