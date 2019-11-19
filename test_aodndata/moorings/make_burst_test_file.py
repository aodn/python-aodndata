#! /usr/bin/env python

# Create test file for burst_average.py testing

from collections import defaultdict
from datetime import timedelta
from numpy import ma

import numpy as np

from netCDF4 import Dataset, num2date

from test_aodndata.moorings.test_burst_average import INPUT_FILE as TEST_FILE

stats = defaultdict(list)


def update_stats(burst, vals, qc):
    """update stats for burst with given values and qc"""
    v = ma.array(vals, mask=(qc>2))
    stats['burst'].append(burst)
    stats['TEMP'].append(v.mean())
    stats['TEMP_burst_min'].append(v.min())
    stats['TEMP_burst_max'].append(v.max())
    stats['TEMP_burst_sd'].append(v.std())
    stats['TEMP_num_obs'].append((~v.mask).sum())
    # print('{b:2} {num:5} {mean:12} {sd:12}'.format(b=burst, num=stats['num'][-1], mean=stats['mean'][-1],
    #                                                sd=stats['sd'][-1])
    #       )


D = Dataset(TEST_FILE, mode='a')

TIME = D['TIME']

# not really needed here, but a nice way to work out burst indices
time = num2date(TIME[:], TIME.units)
difftime = np.diff(time)
skip = np.array([0] + [int(difftime[i] > timedelta(seconds=2)) for i in range(1200)])
bounds = np.flatnonzero(skip)
burst_i = np.cumsum(skip)

TEMP = D['TEMP']
TEMPqc = D['TEMP_quality_control']

# start by clearing everything
TEMP[:] = TEMP._FillValue
TEMPqc[:] = 4

# some bad data  at the start
for j in range(2):
    i = np.flatnonzero(burst_i == j)
    TEMP[i] = 100.
    TEMPqc[i] = 4
    update_stats(j, TEMP[i], TEMPqc[i])
    
# some slightly  better data...
for j in range(2, 4):
    i = np.flatnonzero(burst_i == j)
    TEMP[i] = 20.
    TEMPqc[i] = 3
    update_stats(j, TEMP[i], TEMPqc[i])

# now for some "good" fake data fixed for whole burst
for j in range(4, 6):
    i = np.flatnonzero(burst_i == j)
    TEMP[i] = j
    TEMPqc[i] = 2
    update_stats(j, TEMP[i], TEMPqc[i])

# still fake data but varying, and with some flagged points
for j in range(6, 8):
    i = np.flatnonzero(burst_i == j)
    k = 10*(j-5) + 1
    TEMP[i[:k]] = np.arange(k, dtype=TEMP.dtype) + j
    TEMPqc[i[:k]] = 1
    TEMP[i[k:]] = -2
    TEMPqc[i[k:]] = j-3
    update_stats(j, TEMP[i], TEMPqc[i])


D.close()

for k, v in stats.items():
    m = ma.array(v, fill_value=-999)
    print('{k} = ma.masked_values({v}, -999)'.format(k=k, v=list(m.data)))
