#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


def lin(x,xp,fp,period=None,**kwargs):
    if not period is None:
        xp = np.append(xp[-1]-period,xp)
        fp = np.append(fp[-1],fp)

    return np.interp(x,xp,fp,**kwargs)


def zoh(x,xp,fp,period=None,**kwargs):

    if not period is None:
        xp = np.append(xp[-1]-period,xp)
        fp = np.append(fp[-1],fp)

    ind = np.interp( x, xp, np.arange(len(xp)),**kwargs )
    f = np.array([np.nan if np.isnan(i) else fp[int(i)] for i in ind])
    return f

