# -*- coding: utf-8 -*-
# pyTEA: A tool to enable techno-economic analysis (TEA) in Python.
# Copyright (C) 2023-2024, Sarang S. Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/sarangbhagwat/pyTEA/LICENSE.txt
# for license details.

__version__ = '0.0.1'
__author__ = 'Sarang S. Bhagwat'

# %% Initialize pyTEA 

from . import _TEA

TEA = _TEA.TEA

__all__ = (
    'TEA',
)
