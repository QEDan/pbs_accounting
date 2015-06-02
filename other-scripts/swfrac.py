#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import numpy as np


def main():
    """
    Main routine: Cross reference a list of nodes to find common jobs
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0]  \
                 + ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    swfracs = list()
    for date in joblist:
        datelist = list()
        datelist.append(date)
        jobs = jobstats.alljobs(datelist)
        corehrslt = 0.0
        corehrsgt = 0.0
        for job in jobs:
            if 'sw' in job.queue:
                if job.cores < 12:
                    corehrslt += job.cores*job.walltime
                else:
                    corehrsgt += job.cores*job.walltime
        if corehrslt > 0 and corehrsgt > 0:
            frac = corehrslt/(corehrslt + corehrsgt)
            print(date + " " + str(frac))
            swfracs.append(frac)

    print("===Mean===")
    print(str(np.mean(swfracs)) + "+/-" + str(np.std(swfracs)/len(swfracs)))
                
    return

if __name__ == '__main__':
    main()

            
    
