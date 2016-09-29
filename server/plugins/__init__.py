#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# make some objects from the lib folder available for plugins
sys.path.insert(0, os.path.abspath('..'))

from core.plugin import Plugin
from core.database import Database
