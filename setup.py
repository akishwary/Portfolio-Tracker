# -*- coding: utf-8 -*-
"""
@author: Amrin.Kishwary
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy as np

setup(
      name = "average open price",
      cmdclass = {'build_ext':build_ext},
      include_dirs = [np.get_include()],
      ext_modules = Extension("aop",["aop.pyx"]))
      