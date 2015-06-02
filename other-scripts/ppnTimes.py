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
    qts_ppn = list()
    qts_procs = list()
    corehrs_ppn = list()
    corehrs_procs = list()
    for job in jobs:
        if job.cores > 1 and job.tiq > 0 and not np.isnan(job.tiq):
            if job.ppn == 0:
                qts_procs.append(np.log10(job.tiq/3600.0))
                corehrs_procs.append(np.log10(job.cores*job.walltimereq/3600.0))
            else:
                qts_ppn.append(np.log10(job.tiq/3600.0))
                corehrs_ppn.append(np.log10(job.cores*job.walltimereq/3600.0))

    subx_procs = list()
    suby = list()
    for i,j in zip(corehrs_procs,qts_procs):
        if j > -1.0 and i > -1.0:
            subx_procs.append(i)
            suby.append(j)
    z_procs = np.polyfit(subx_procs,suby,1)
    p_procs = np.poly1d(z_procs)
    print(z_procs)
    
    subx_ppn = list()
    suby = list()
    for i,j in zip(corehrs_ppn, qts_ppn):
        if j > -1.0 and i > -1.0:
            subx_ppn.append(i)
            suby.append(j)
    z_ppn = np.polyfit(subx_ppn,suby,1)
    p_ppn = np.poly1d(z_ppn)
    print(z_ppn)
        

    plt.cla()
    plt.hexbin(corehrs_procs, qts_procs, bins='log')
    #plt.plot([min(corehrs_procs), max(corehrs_procs)], [min(qts_procs), max(qts_procs)], 'k--')
    plt.plot(subx_ppn, p_ppn(subx_ppn), 'y', linewidth=4)
    plt.plot(subx_procs, p_procs(subx_procs), 'w', linewidth=4)
    plt.xlabel('log(Core hours requested)')
    plt.ylabel('log(Queue Time (hours))')
    plt.savefig('procs.png')



    plt.cla()
    plt.hexbin(corehrs_ppn, qts_ppn, bins='log')
#    plt.plot([min(qts_ppn), max(qts_ppn)], [min(qts_ppn), max(qts_ppn)], 'k--')
    plt.plot(subx_procs, p_procs(subx_procs), 'w', linewidth=4)
    plt.plot(subx_ppn, p_ppn(subx_ppn),'y', linewidth=4)
    plt.xlabel('log(Core hours requested)')
    plt.ylabel('log(Queue Time (hours))')
    plt.savefig('ppn.png')

if __name__ == '__main__':
    main()

            
    
