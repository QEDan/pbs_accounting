#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import numpy as np


def main():
    """
    Main routine: Process total core days used by all jobs
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0]  \
                 + ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    jobs = jobstats.alljobs(joblist)

    coredays = 0.0
    for job in jobs:
        coredays += job.cores*job.walltime
    coredays /= 24.0*3600.0
    print( '%.1f' %coredays)


    return

if __name__ == '__main__':
    main()

            
    
