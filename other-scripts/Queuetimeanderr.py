#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys
import numpy as np
import pylab as plt

def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0] +  ' [Accounting files]')
    else:
        joblist = sys.argv[1:]


    jobs = jobstats.alljobs(joblist)
    qts = [job.tiq for job in jobs]
    if len(qts) > 0:
        meanqt = np.mean(qts)
        if(meanqt) > 0.0:
            errqt = np.std(qts)/np.sqrt(len(qts))
            print(str(joblist).strip("[]'/tmp") + ' ' + str(meanqt) + ' ' + str(errqt))

if __name__ == '__main__':
    main()

            
    
