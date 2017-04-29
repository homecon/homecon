#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
import subprocess
import shutil
import getpass
import pyomo.environ as pyomo



basedir = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),'..','..')
username = 'homecon'


################################################################################
# userdata
################################################################################

def create_user():
    res = subprocess.call(['sudo', 'id', '-u', username],stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if res == 1:
        password = getpass.getpass('Password:')
        password2 = getpass.getpass('Repeat password:')

        if password == password2:
            subprocess.call(['sudo', 'useradd', username ])
            subprocess.call(['sudo', 'echo', '-e', '"{}\n{}\n"'.format(password,password), '|', 'passwd', username])
        else:
            raise Exception('Passwords did not match')


def create_data_folders():

    # create the data folder
    subprocess.call(['sudo', 'mkdir', '-p', '/var/lib/homecon'])
    subprocess.call(['sudo', 'chown', '{}:{}'.format(username,username) , '/var/lib/homecon'])

    # create the log folder
    subprocess.call(['sudo', 'mkdir', '-p', '/var/log/homecon'])
    subprocess.call(['sudo', 'chown', '{}:{}'.format(username,username) , '/var/log/homecon'])

    # create the app folder
    subprocess.call(['sudo', 'mkdir', '-p', '/var/www/homecon'])
    subprocess.call(['sudo', 'chown', '{}:{}'.format(username,username) , '/var/www/homecon'])
    subprocess.call(['sudo', 'chmod', '755' , '/var/www/homecon'])

    # copy the app files
    subprocess.call(['sudo', 'cp', '{}/homecon/app/build/bundled'.format(sys.prefix) , '/var/www/homecon'])



def set_static_ip(ip=None):

    currentdir = os.getcwd()
    os.chdir(basedir)

    if ip is None:
        rawip = input('Enter the desired static ip address (192.168.1.234): ')
        if rawip == '':
            ip = '192.168.1.234'
        else:
            ip = rawip

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

    os.chdir(currentdir)


def patch_pyutilib():
    path = os.path.join(sys.prefix,'lib','python{}'.format(sys.version[:3]),'site-packages','pyutilib','subprocess','processmngr.py')
    origpath = path.replace('.py','_orig.py')

    if not os.path.exists(origpath):
        shutil.copyfile(path,origpath)

    with open(path,'w') as f:
        with open(origpath,'r') as f_orig:

            for i,l in enumerate(f_orig):
                if i+1 not in [496,497,498,499,500,501,502,503,504,505,506,507,508,509]:
                    f.write(l)



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

    # get compilation dependencies
    subprocess.call(['sudo', 'apt-get', '-y', 'install', 'gcc', 'g++', 'gfortran', 'wget'])


    installdir = '/usr/local/glpk'
    installver = '4.60'

    if not os.path.exists(installdir):
        subprocess.call(['sudo', 'mkdir', installdir])
        
    os.chdir(installdir)

    if not os.path.exists('glpk-{}'.format(installver)):

        if not os.path.exists('glpk-{}.tar.gz'.format(installver)):
            subprocess.call(['sudo', 'wget', 'http://ftp.gnu.org/gnu/glpk/glpk-{}.tar.gz'.format(installver)])

        subprocess.call(['sudo', 'tar', 'xvf', 'glpk-{}.tar.gz'.format(installver)])
    
    os.chdir('glpk-{}'.format(installver))

    subprocess.call(['sudo', './configure'])
    subprocess.call(['sudo', 'make'])
    subprocess.call(['sudo', 'make', 'check'])
    subprocess.call(['sudo', 'make', 'install'])
    subprocess.call(['sudo', 'ldconfig', '/usr/local/lib'])

    os.chdir(currentdir)



def install_ipopt():
    """
    get and compile ipopt
    """

    currentdir = os.getcwd()
    os.chdir(basedir)

    # get compilation dependencies
    subprocess.call(['apt-get', '-y', 'install', 'gcc', 'g++', 'gfortran', 'patch', 'wget'])

    installdir = '/usr/local/ipopt'
    installver = '3.12.7'

    if not os.path.exists(installdir):
        subprocess.call(['sudo', 'mkdir', installdir])

    os.chdir(installdir)

    if not os.path.exists('Ipopt-{}'.format(installver)):

        if not os.path.exists('Ipopt-{}.tgz'.format(installver)):
            subprocess.call(['sudo', 'wget', 'http://www.coin-or.org/download/source/Ipopt/Ipopt-{}.tgz'.format(installver)])

        subprocess.call(['sudo', 'tar', 'xvf', 'Ipopt-{}.tgz'.format(installver)])

    os.chdir('Ipopt-{}'.format(installver))

    # get third party packages
    os.chdir('ThirdParty/Blas')
    subprocess.call(['sudo', './get.Blas'])
    os.chdir('../..')

    os.chdir('ThirdParty/Lapack')
    subprocess.call(['sudo', './get.Lapack'])
    os.chdir('../..')

    os.chdir('ThirdParty/ASL')
    subprocess.call(['sudo', './get.ASL'])
    os.chdir('../..')

    os.chdir('ThirdParty/Mumps')
    subprocess.call(['sudo', './get.Mumps'])
    os.chdir('../..')

    os.chdir('ThirdParty/Metis')
    subprocess.call(['sudo', './get.Metis'])
    os.chdir('../..')

    # compiling ipopt
    if not os.path.exists('build'):
        os.mkdir('build')

    os.chdir('build')

    subprocess.call(['sudo', '../configure', '--prefix=/usr/local/', '-C', 'ADD_CFLAGS=-DNO_fpu_control'])
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

    # get compilation dependencies
    subprocess.call(['sudo', 'apt-get', '-y', 'install', 'gcc', 'g++', 'wget'])

    installdir = '/usr/local/bonmin'
    installver = '1.8.4'

    if not os.path.exists(installdir):
        subprocess.call(['sudo', 'mkdir', installdir])

    os.chdir(installdir)

    if not os.path.exists('Bonmin-{}'.format(installver)):

        if not os.path.exists('Bonmin-{}.tgz'.format(installver)):
            subprocess.call(['wget', 'https://www.coin-or.org/download/source/Bonmin/Bonmin-{}.tgz'.format(installver)])

        subprocess.call(['tar', 'xvf', 'Bonmin-{}.tgz'.format(installver)])

    os.chdir('Bonmin-{}'.format(installver))

    # get third party packages
    os.chdir('ThirdParty/Blas')
    subprocess.call(['sudo', './get.Blas'])
    os.chdir('../..')

    os.chdir('ThirdParty/Lapack')
    subprocess.call(['sudo', './get.Lapack'])
    os.chdir('../..')

    os.chdir('ThirdParty/ASL')
    subprocess.call(['sudo', './get.ASL'])
    os.chdir('../..')

    os.chdir('ThirdParty/Mumps')
    subprocess.call(['sudo', './get.Mumps'])
    os.chdir('../..')

    os.chdir('ThirdParty/Metis')
    subprocess.call(['sudo', './get.Metis'])
    os.chdir('../..')

    # compiling bonmin
    if not os.path.exists('build'):
        os.mkdir('build')

    os.chdir('build')

    subprocess.call(['sudo', '../configure', '--prefix=/usr/local/', '-C'])
    subprocess.call('sudo', ['make'])
    subprocess.call(['sudo', 'make', 'test'])
    subprocess.call(['sudo', 'make', 'install'])

    os.chdir(currentdir)
