#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

import os
import inspect
import subprocess
import shutil
import pyomo.environ as pyomo


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



basedir = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),'..','..')
os.chdir(basedir)

def set_static_ip(ip):


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



def install_glpk():
    """
    Get and compile glpk
    """

    currentdir = os.getcwd()
    os.chdir(basedir)

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

    os.chdir(currentdir)



def install_ipopt():
    """
    get and compile ipopt
    """

    currentdir = os.getcwd()
    os.chdir(basedir)

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

    os.chdir(currentdir)

