#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


def lin(x,xp,fp,**kwargs):

    return np.interp(x,xp,fp,**kwargs)


def zoh(x,xp,fp,**kwargs):

    ind = np.interp( x, xp, np.arange(len(xp)),**kwargs )
    f = np.array([np.nan if np.isnan(i) else fp[int(i)] for i in ind])
    return f

