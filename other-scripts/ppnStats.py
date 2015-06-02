#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys

def main():
    """
    Main routine: Print stats about ppn usage
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0] \
                 + ' [Accounting files]')
    else:
        joblist = sys.argv[1:]

    usernames = {}
    jobs = jobstats.alljobs(joblist)
    for job in jobs:
        if job.user in usernames:
            usernames[job.user].addJob(job)
        else:
            usernames[job.user] = jobstats.userClass(job)

    
    for user in sorted(usernames):
        if any(1 < job.ppn < 12 for job in usernames[user].joblist):
            print(user + ':')
            usernames[user].printTopProp('ppn')

    return

if __name__ == '__main__':
    main()

            
    
