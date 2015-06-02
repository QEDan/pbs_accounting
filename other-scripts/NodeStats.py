#!/software/tools/python-2.6.7/bin/python
import jobstats
import sys

def main():
    """
    Main routine: Print User stats
    """
    if len(sys.argv) < 2:
        sys.exit('Usage: ' + sys.argv[0] +  ' [Accounting files]')
    else:
        joblist = sys.argv[1:]


    jobs = jobstats.alljobs(joblist)
    nodes = {}
    for job in jobs:
        if 'debug' not in job.queue and \
               'lmgpu' not in job.queue and \
               'scalemp' not in job.queue and \
               'class' not in job.queue:
            for node in job.nodes:
                if node not in nodes:
                    nodes[node] = jobstats.nodeClass(job, node)
                else:
                    nodes[node].joblist.append(job)
    for node in nodes:
        if len(nodes[node].joblist) > 20 and \
           (nodes[node].avgEfficiency() < 0.1 or \
           nodes[node].fractionBad() > 0.9):
               nodes[node].printStats()
if __name__ == '__main__':
    main()

            
    
