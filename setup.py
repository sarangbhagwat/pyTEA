# -*- coding: utf-8 -*-
# teamod: Modules to enable techno-economic analysis (TEA) in Python.
# Copyright (C) 2023-2024, Sarang S. Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/sarangbhagwat/teamod/LICENSE.txt
# for license details.
"""
@author: sarangbhagwat
"""

from setuptools import setup

setup(
    name='teamod',
    packages=['teamod'],
    version='0.0.1',    
    description='A tool to enable techno-economic analysis (TEA) in Python.',
    url='https://github.com/sarangbhagwat/teamod/',
    author='Sarang S. Bhagwat',
    author_email='sarang.bhagwat.git@gmail.com',
    license='MIT',
    # packages=['contourplots'],
    install_requires=[
                      'numpy>=1.24.4',       
                      'pandas>=1.5.3',
                      'scipy>=1.10.1'
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: University of Illinois/NCSA Open Source License',  
        'Operating System :: Microsoft :: Windows',        
        'Programming Language :: Python :: 3.9'
    ],
)
