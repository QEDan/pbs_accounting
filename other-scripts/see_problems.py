#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys

def main():
    """
    Main routine: Show information about jobs with negative exit codes
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0] \
                 + ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    probjobs = None
    jobs = jobstats.alljobs(joblist)
    for job in jobs:
        if job.efficiency() > 10000.0:
            print(str(job.id) + " " + str(job.efficiency()))
        if job.exitcode < 0:
            if probjobs != None:
                probjobs.addJob(job)
            else:
                probjobs = jobstats.jobGroup(job)

    probjobs.printStats()
    print("Top Users:")
    probjobs.printTopProp('user')
    print("Top Nodes:")
    probjobs.printTopProp('node')
    print("Top Queues:")
    probjobs.printTopProp('queue')
    print("Top Exit Codes:")
    probjobs.printTopProp('exitcode')
    print("Super efficient Jobs:")
    probjobs.printSuperEff()
    jobs.printSuperEff()

    return

if __name__ == '__main__':
    main()

            
    
