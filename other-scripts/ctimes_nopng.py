#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import numpy as np
import pylab as plt
import datetime as dt
import time

def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0] +  ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    reset_time = dt.datetime(2013, 05, 10, 19, 30)
    reset_time_unix = time.mktime(reset_time.timetuple())
    crash_times = list()
    crash_times.append(dt.datetime(2013, 05, 11, 0, 50))
    crash_times.append(dt.datetime(2013, 05, 11, 7, 00))
    crash_times.append(dt.datetime(2013, 05, 11, 7, 25))
    crash_times.append(dt.datetime(2013, 05, 11, 8, 18))
    crash_times.append(dt.datetime(2013, 05, 11, 8, 50))
    crash_times.append(dt.datetime(2013, 05, 11, 10, 55))
    crash_times.append(dt.datetime(2013, 05, 13, 2, 43))
    crash_times.append(dt.datetime(2013, 05, 13, 6, 46))
    crash_times.append(dt.datetime(2013, 05, 13, 7, 14))
    crash_times.append(dt.datetime(2013, 05, 13, 11, 31))
    crash_times.append(dt.datetime(2013, 05, 13, 11, 41))
    crash_times.append(dt.datetime(2013, 05, 13, 11, 55))
    crash_times_unix = list()
    for ct in crash_times:
        crash_times_unix.append(time.mktime(ct.timetuple()))

    jobs = jobstats.alljobs(joblist)
    ctimes = list()
    etimes = list()
    qtimes = list()
    starts = list()
    ends = list()
    for job in jobs:
        if job.ctime > reset_time_unix and job.start > 0:
            print(job.start)
            if job.ctime < 0 or job.etime < 0 or job.qtime < 0 or job.start < 0 or job.end < 0:
                print(job.id)
            
            ctimes.append(job.ctime)
            etimes.append(job.etime)
            qtimes.append(job.qtime)
            starts.append(job.start)
            ends.append(job.end)

    plt.cla()
    f, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, sharex=True, sharey=False, figsize=(20, 10))
    ax1.hist(ctimes, bins=(max(ctimes) - min(ctimes))/900, color='k', label='Created')
    ax1.vlines(crash_times_unix, 0, ax1.get_ylim()[1], 'b')
    ax1.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    ax2.hist(etimes, bins=(max(etimes) - min(etimes))/900, color='k', label='Eligible')
    ax2.vlines(crash_times_unix, 0, ax2.get_ylim()[1], 'b')
    ax2.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)

    ax3.hist(qtimes, bins=(max(qtimes) - min(qtimes))/900, color='k', label='Queued')
    ax3.vlines(crash_times_unix, 0, ax3.get_ylim()[1], 'b')
    ax3.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    ax4.hist(starts, bins=(max(starts) - min(starts))/900, color='k', label='Started')
    ax4.vlines(crash_times_unix, 0, ax4.get_ylim()[1], 'b')
    ax4.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    ax5.hist(ends, bins=(max(ends) - min(ends))/900, color='k', label='Finished')
    ax5.vlines(crash_times_unix, 0, ax5.get_ylim()[1], 'b')
    ax5.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    plt.xlabel('Unix Epoch Time')
    f.subplots_adjust(hspace=0, right=0.8)
    plt.savefig('ctimes.temp.png')

if __name__ == '__main__':
    main()

            
    
