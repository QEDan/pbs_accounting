#!/software/tools/python-2.6.7/bin/python

import numpy as np
import matplotlib.pylab as plt

file = open('Queuetimevsday_hb.dat')

qts = list()
qterrs = list()
dates = list()
for line in file.readlines():
    dates.append(line.split(' ')[0][4:])
    qts.append(float(line.split(' ')[1])/3600.0)
    qterrs.append(float(line.split(' ')[2])/3600.0)

plt.cla()
plt.errorbar(range(len(qts)), qts, qterrs, fmt='k.')
plt.ylabel('Mean queue time (hours)')
plt.xticks(range(len(qts))[1::30], dates[1::30])
plt.xlabel('Day')
plt.savefig('qtvsday_hb.png')
