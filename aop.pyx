"""
@author: Amrin.Kishwary

This is a function that calculates average open price per transactions.
The code is written in cython for speed.
col_c = condition, col_q = quantity, col_p = price, col_lp= lagged position
aop = average opening price

"""
import cython
cimport numpy as np #import numpy
import numpy as np

cpdef np.ndarray[double] ave_open_price(np.ndarray col_c, np.ndarray col_q, np.ndarray col_p, np.ndarray col_lp):
    
    assert (col_c.dtype == np.int64 and col_q.dtype == np.int64 and col_p.dtype == np.float64 and col_lp.dtype == np.float64)
    cdef Py_ssize_t i, n = len(col_c)
    assert (len(col_q) == len(col_p) == len(col_lp) == n)
    cdef np.ndarray[double] r = np.empty(n)
    r[0]=col_p[0]
    for i in range(len(col_c)):
        if col_c[i] == 1:
            r[i] = col_p[i]
        elif col_c[i] == 4:
            r[i] = col_p[i]
        elif col_c[i]==5:
            r[i] = 0
        elif col_c[i]==3:
            r[i] = r[i-1]
        else:
            r[i]=((col_q[i]*col_p[i])+(col_lp[i]*r[i-1]))/(col_q[i]+col_lp[i])
    return r