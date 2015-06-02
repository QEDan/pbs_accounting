#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import operator

def main():
    """
    Main routine: Print User stats
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0]  \
                 + ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    exitCodes = {}
    jobs = jobstats.alljobs(joblist)
    for job in jobs:
        if  job.exitcode not in exitCodes:
            exitCodes[job.exitcode] = 1
        else:
            exitCodes[job.exitcode] += 1
            
    sortedecs = sorted(exitCodes.iteritems(), key=operator.itemgetter(1))

    for ec, quant in sortedecs:
        print ec, 100.0*quant/len(jobs)
    return

if __name__ == '__main__':
    main()

            
    
