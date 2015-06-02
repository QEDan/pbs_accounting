#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys

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
    for job in jobs:
        if username in job.user:
            if user == None:
                user = jobstats.user(job)
            else:
                user.addJob(job)
    user.printStats()
    return

if __name__ == '__main__':
    main()

            
    
