#!/usr/bin/env python
import jobstats
import sys
import numpy as np
from optparse import OptionParser
import datetime as dt


def getepoch(time):
    #Returns the Unix Epoch time
    return (time - dt.datetime(1970,1,1)).total_seconds()

def gettime(timein, datein):
    #Converts a string (HH:MM:SS) and datetime.date or a Unix Epoch time to a Unix Epoch time.
    error = "Invalid time submitted. Please use HH:MM:SS format or unix epoch time"
    if datein == None:
        date = dt.date.today()
    else:
        datestring = datein.split("-")
        try:
            date = dt.date(int(datestring[0]), int(datestring[1]), int(datestring[2]))
        except:
            sys.exit(error)
    if ":" in timein:
        timestring = timein.split(":")
        try:
            dttime = dt.time(int(timestring[0]),int(timestring[1]),int(timestring[2]))
        except:
            sys.exit(error)
        timeout = dt.datetime(date.year, date.month, date.day, dttime.hour, dttime.minute, dttime.second)
        timeout = int(getepoch(timeout))
    else:
        #assume unix epoch time
        try:
            timeout = int(timein)
        except:
            sys.exit(error)
    return timeout


def main():
    """
    Main routine: Scans through jobs and identifies jobs that were running at the specified time
    """
    #Parse command-line options
    usage = "usage: %prog [options] [time (HH:MM:DD or Epoch time)] [Accounting files]"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--node", dest="node", action="append",\
                          type="string", help="Search only for specified node(s)")
    parser.add_option("-d", "--date", dest="date", action="store",\
                          type="string", help="Specify a date in YYYY-MM-DD format (default: today)")
    parser.add_option("-s", "--summary", dest="summarize", action="store_true",\
                          default=False, help="Print a summary of each job (default: jobID only)")

    (options, args) = parser.parse_args()
    
    if len(args) < 2:
        sys.exit(usage + '\n --help for list of options')
    else:
        time = gettime(args[0], options.date)
        joblist = args[1:]

    #Filters prevent storing undesired jobs in the jobs list
    filters = None
    if options.node != None:
        filters = options.node
    jobs = jobstats.alljobs(joblist, filters)


    for job in jobs:
        if job.wasRunningAt(time):
            #Skip jobs on nodes that weren't specified
            if options.node != None:
                if not any(n in job.nodes for n in options.node):
                    continue
            if options.summarize:
                job.printStats()
            else:
                print job.id


    return

if __name__ == '__main__':
    main()

            
    
