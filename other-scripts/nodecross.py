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
        joblist = sys.argv[2:]

    jobs = jobstats.alljobs(joblist)
    nodelist = ['sw-2r13-n50', 'sw-2r13-n51', 'sw-2r14-n20', 'sw-2r15-n17', 'sw-2r15-n44', 'sw-2r15-n66']
    
    print('cross referencing nodes:')
    print(nodelist)
    for job in jobs:
        if all(node in job.nodes for node in nodelist):
            job.printStats()

    return

if __name__ == '__main__':
    main()

            
    
