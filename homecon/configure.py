#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
import subprocess
import shutil
import getpass
import pyomo.environ as pyomo

basedir = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), '..', '..')
username = 'homecon'


def create_data_folders():
    # create the data folder
    try:
        os.makedirs(os.path.join(sys.prefix, 'lib/homecon'))
    except:
        pass
    # create a temp folder
    try:
        os.makedirs(os.path.join(sys.prefix, 'var/tmp/homecon'))
    except:
        pass
    # create the log folder
    try:
        os.makedirs(os.path.join(sys.prefix, 'log/homecon'))
    except:
        pass


def set_static_ip(ip=None):
    """
    Notes
    -----
    needs superuser privileges

    """
    try:
        if ip is None:
            rawip = input('Enter the desired static ip address (192.168.1.234): ')
            if rawip == '':
                ip = '192.168.1.234'
            else:
                ip = rawip

        splitip = ip.split('.')

        if not len(splitip) == 4:
            raise Exception('{} is not a valid ip address'.format(ip))

        with open(os.path.join(sys.prefix, 'var', 'tmp', 'homecon', 'network_template'), 'r') as f:
            content = f.read()

            with open(os.path.join(sys.prefix, 'var', 'tmp', 'homecon', 'interfaces'), 'w') as fw:
                fw.write(content.format(ip=ip, ip0=splitip[0], ip1=splitip[1]))

        subprocess.call(['sudo', 'mv', os.path.join(sys.prefix, 'var', 'tmp', 'homecon', 'interfaces'),
                         '/etc/network/interfaces'])
    except:
        print('Warning: Could not set static ip address')


def set_init_script(scriptname='homecon'):
    try:
        with open(os.path.join(sys.prefix, 'var', 'tmp', 'homecon', 'init_template'), 'r') as f:
            content = f.read()

            with open(os.path.join(sys.prefix, 'var', 'tmp', 'homecon', scriptname), 'w') as fw:
                fw.write(content.format(bin=os.path.join(sys.prefix, 'bin')))

        subprocess.call(['sudo', 'mv', os.path.join(sys.prefix, 'var', 'tmp', 'homecon',scriptname),
                         os.path.join('/etc/init.d',scriptname)])
        subprocess.call(['sudo', 'chmod', '755', os.path.join('/etc/init.d', scriptname)])
        subprocess.call(['sudo', 'chown', 'root:root', os.path.join('/etc/init.d', scriptname)])
        subprocess.call(['sudo', 'update-rc.d', scriptname, 'defaults'])
    except:
        print('Warning: Could not create init script')


def patch_pyutilib():
    try:
        path = os.path.join(sys.prefix, 'lib', 'python{}'.format(sys.version[:3]),
                            'site-packages', 'pyutilib', 'subprocess', 'processmngr.py')

        if not os.path.exists(path):
            for temppath in os.listdir(os.path.join(sys.prefix, 'lib', 'python{}'.format(sys.version[:3]),
                                                    'site-packages')):
                if temppath.startswith('PyUtilib'):
                    path = os.path.join(sys.prefix, 'lib', 'python{}'.format(sys.version[:3]), 'site-packages',
                                        temppath, 'pyutilib', 'subprocess', 'processmngr.py')
                    break

        origpath = path.replace('.py', '_orig.py')

        if not os.path.exists(origpath):
            shutil.copyfile(path, origpath)

        with open(path, 'w') as f:
            with open(origpath, 'r') as f_orig:

                for i, l in enumerate(f_orig):
                    if i+1 not in [496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509]:
                        f.write(l)
    except:
        print('Warning: Could not patch pyutilib')


################################################################################
# Plugin dependencies
################################################################################
def install_knxd():
    """
    https://github.com/knxd/knxd
    """
    try:
        currentdir = os.getcwd()
        installdir = '{}/local/knxd'.format(sys.prefix)
        if not os.path.exists(installdir):
            os.makedirs(installdir)
        os.chdir(installdir)

        subprocess.call(['git', 'clone', 'https://github.com/knxd/knxd.git'])
        os.chdir('knxd')
        subprocess.call(['dpkg-buildpackage' '-b' '-uc'])
        os.chdir(installdir)
        subprocess.call(['sudo', 'dpkg', '-i', 'knxd_*.deb', 'knxd-tools_*.deb'])
    except:
        print('Warning: Could not install knxd')
    finally:
        os.chdir(currentdir)


################################################################################
# Optimization solvers
################################################################################
model = pyomo.ConcreteModel()
model.x = pyomo.Var(domain=pyomo.NonNegativeReals)
model.y = pyomo.Var(domain=pyomo.NonNegativeReals)
model.Constraint1 = pyomo.Constraint(expr=model.y >= 4-2*model.x)
model.Objective = pyomo.Objective(rule=lambda model: model.x+model.y)


def solver_available(solver):
    """
    Tests if a solver is available for pyomo
    
    """
    
    try:
        optimizer = pyomo.SolverFactory(solver)
        results = optimizer.solve(model)
        return True   
    except:
        return False


def install_glpk():
    """
    Get and compile glpk
    """

    currentdir = os.getcwd()
    os.chdir(basedir)

    installdir = '{}/local/glpk'.format(sys.prefix)
    installver = '4.60'

    if not os.path.exists(installdir):
        os.makedirs(installdir)

    os.chdir(installdir)

    if not os.path.exists('glpk-{}'.format(installver)):

        if not os.path.exists('glpk-{}.tar.gz'.format(installver)):
            subprocess.call([ 'wget', 'http://ftp.gnu.org/gnu/glpk/glpk-{}.tar.gz'.format(installver)])

        subprocess.call(['tar', 'xvf', 'glpk-{}.tar.gz'.format(installver)])
    
    os.chdir('glpk-{}'.format(installver))

    subprocess.call(['sudo', './configure', '--prefix={}'.format('/usr/local/bin')])
    subprocess.call(['sudo', 'make'])
    subprocess.call(['sudo', 'make', 'check'])
    subprocess.call(['sudo', 'make', 'install'])
    subprocess.call(['sudo', 'ldconfig', '{}'.format('/usr/local/bin')])

    os.chdir(currentdir)

def install_ipopt():
    """
    get and compile ipopt
    """

    currentdir = os.getcwd()
    os.chdir(basedir)

    installdir = '{}/local/ipopt'.format(sys.prefix)
    installver = '3.12.7'

    if not os.path.exists(installdir):
        os.makedirs(installdir)

    os.chdir(installdir)

    if not os.path.exists('Ipopt-{}'.format(installver)):

        if not os.path.exists('Ipopt-{}.tgz'.format(installver)):
            subprocess.call(['wget', 'http://www.coin-or.org/download/source/Ipopt/Ipopt-{}.tgz'.format(installver)])

        subprocess.call(['tar', 'xvf', 'Ipopt-{}.tgz'.format(installver)])

    os.chdir('Ipopt-{}'.format(installver))

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

    subprocess.call(['sudo', '../configure', '--prefix={}'.format('/usr/local/bin'), '-C', 'ADD_CFLAGS=-DNO_fpu_control'])
    subprocess.call(['sudo', 'make'])
    subprocess.call(['sudo', 'make', 'test'])
    subprocess.call(['sudo', 'make', 'install'])

    os.chdir(currentdir)


def install_bonmin():
    """
    get and compile bonmin
    """

    currentdir = os.getcwd()
    os.chdir(basedir)

    installdir = '{}/local/bonmin'.format(sys.prefix)
    installver = '1.8.4'

    if not os.path.exists(installdir):
        os.makedirs(installdir)

    os.chdir(installdir)

    if not os.path.exists('Bonmin-{}'.format(installver)):

        if not os.path.exists('Bonmin-{}.tgz'.format(installver)):
            subprocess.call(['wget', 'https://www.coin-or.org/download/source/Bonmin/Bonmin-{}.tgz'.format(installver)])

        subprocess.call(['tar', 'xvf', 'Bonmin-{}.tgz'.format(installver)])

    os.chdir('Bonmin-{}'.format(installver))

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

    # compiling bonmin
    if not os.path.exists('build'):
        os.mkdir('build')

    os.chdir('build')

    subprocess.call(['sudo', '../configure', '--prefix={}'.format('/usr/local/bin'), '-C', 'ADD_CFLAGS=-DNO_fpu_control'])
    subprocess.call(['sudo', 'make'])
    subprocess.call(['sudo', 'make', 'test'])
    subprocess.call(['sudo', 'make', 'install'])

    os.chdir(currentdir)
