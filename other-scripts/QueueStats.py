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
        queue = sys.argv[1]
        joblist = sys.argv[2:]


    jobs = jobstats.alljobs(joblist)
    qnum = 0

    print('searching queue ' + queue)
    for job in jobs:
        if queue in job.queue:
            qnum += 1
    print('Queue ' + queue + ' used in ' + str(qnum) \
          + ' of ' + str(len(jobs)) + ' jobs') 
    return

if __name__ == '__main__':
    main()

            
    
