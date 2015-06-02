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
    qts = list()
    wallts = list()
    corehrs = list()
    allqts = list()
    for job in jobs:
        if job.cores > 1 and job.tiq > 0 and not np.isnan(job.tiq):
            allqts.append(np.log10(job.tiq/3600.0))
            corehrs.append(np.log10(job.cores*job.walltimereq/3600.0))
        if job.cores == 1 and job.tiq > 0 and not np.isnan(job.tiq):
            qts.append(np.log10(job.tiq/3600.0))
            wallts.append(np.log10(job.walltimereq/3600.0))
    print('max qt:' + str(max(qts)))
    print('avg qt:' + str(np.mean(qts)) + '+/-' + str(np.std(qts)/np.sqrt(len(qts))))

    subx = list()
    suby = list()
    for i,j in zip(wallts,qts):
        if j > -1.0 and i > -1.0:
            subx.append(i)
            suby.append(j)
    z = np.polyfit(subx,suby,1)
    p = np.poly1d(z)
    
        

    plt.cla()
    plt.hexbin(wallts, qts, bins='log')
    plt.plot([min(qts), max(qts)], [min(qts), max(qts)], 'k--')
    plt.plot(subx, p(subx), 'k')
    plt.xlabel('log(Walltime (hours))')
    plt.ylabel('log(Queue Time (hours))')
    plt.savefig('QueueTimes.png')

    subx = list()
    suby = list()
    for i,j in zip(corehrs,allqts):
        if j > -1.0 and i > -1.0:
            subx.append(i)
            suby.append(j)
    z = np.polyfit(subx,suby,1)
    p = np.poly1d(z)


    plt.cla()
    plt.hexbin(corehrs, allqts, bins='log')
    plt.plot([min(allqts), max(allqts)], [min(allqts), max(allqts)], 'k--')
    plt.plot(subx, p(subx),'k')
    plt.xlabel('log(Core Hours)')
    plt.ylabel('log(Queue Time (hours))')
    plt.savefig('CHvsQT.png')

if __name__ == '__main__':
    main()

            
    
