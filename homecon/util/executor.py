#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import concurrent.futures
import asyncio
from threading import Timer



_loop = asyncio.get_event_loop()
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)



def run_in_executor(func,*args,**kwargs):
    """
    """
    #_loop.run_in_executor(_executor,func,*args,**kwargs)
    _executor.submit(func,*args,**kwargs)



_debounce_dict = {}

def debounce(delay,function,*args,**kwargs):
    """
    Function used to debounce a function.

    When debounce is called a timer starts running. If the timer reaches zero
    the function is executed. If before the timer reaches zero debounce is
    called again with the same function, the timer is stopped and a new timer
    is started.

    Parameters
    ----------
    delay : number
        The delay in seconds
    
    function : function
        The function to run

    *args, **kwargs : 
        Parameters passed to the function

    """

    def run():
        logging.debug('Running debounced function {}'.format(str(function)))
        function(*args,**kwargs)

    if function in _debounce_dict:
        _debounce_dict[function].cancel()
        del _debounce_dict[function]
        logging.debug('Canceled debounced function {}'.format(str(function)))

    t = Timer(delay,run)
    t.start()
    _debounce_dict[function] = t
    logging.debug('Scheduled debounced function {}'.format(str(function)))



