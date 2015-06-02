#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import matplotlib.pylab as plt
import numpy as np

def main():
    """
    Main routine: Print User stats
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0] +  ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    corehours = np.zeros(1000)
    jobs = jobstats.alljobs(joblist)
    for job in jobs:
        if job.cores < 1000:
            corehours[job.cores] += job.cores*job.walltime/3600.0
    
    plt.cla()
    plt.bar(range(1,1001), list(corehours))
    plt.xlabel('Cores')
    plt.ylabel('Core hours')
    plt.savefig('corehoursvprocs.png')
    return

if __name__ == '__main__':
    main()

            
    
