#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import numpy as np


def main():
    """
    Main routine: Print User stats
    """
    if len(sys.argv) < 3:
        sys.exit('Usage: ' + sys.argv[0] + ' username ' \
                 + ' [Accounting files]')
    else:
        username = sys.argv[1]
        joblist = sys.argv[2:]

    user = None
    jobs = jobstats.alljobs(joblist)
    qtimes = list()
    for job in jobs:
        if username in job.user:
            qtimes.append(job.tiq)
            if user == None:
                user = jobstats.userClass(job)
            else:
                user.addJob(job)
    user.printAllJobs()
    print("mean qtime: (" + str(np.mean(qtimes)/3600.0) + " +/- " \
          + str(np.std(qtimes)/(np.sqrt(len(qtimes))*3600.0)) + ") hours")
    print("max qtime: " + str(max(qtimes)/3600.0) + " hours")
    print("number of jobs: " + str(len(user.joblist)))
    return

if __name__ == '__main__':
    main()

            
    
