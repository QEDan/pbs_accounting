#!/usr/bin/env python
#Script for analyzing the PBS accounting files
#Print statistics for users, queues, nodes, or jobs
#Print a sorted list of user statistics
#See usage summary
import numpy as np
import pylab as plt
import sys
from optparse import OptionParser



def ec2str(exitCode):
#Returns a descriptive string from an exitCode
    if exitCode == 0:
        return 'Job Success'
    elif exitCode == -11:
        return 'JOB_EXEC_RERUN: Job was rerun'
    elif exitCode == -10:
        return 'JOB_EXEC_FAILUID: Invalid UID/GID for job'
    elif exitCode == -4:
        return 'JOB_EXEC_INITABT : Job aborted on MOM initialization'
    elif exitCode == -3:
        return 'JOB_EXEC_RETRY:  job execution failed, do retry'
    elif exitCode ==-2:
        return 'JOB_EXEC_FAIL2 : Job exec failed, after files, no retry'
    elif exitCode == -1:
        return 'JOB_EXEC_FAIL1 : Job exec failed, before files, no retry'
    elif exitCode == 1:
        return 'General Error'
    elif 2 <= exitCode <= 127:
        return 'Exit value of last command in jobscript'
    elif exitCode == 128:
        return 'Invalid argument to exit()'
    elif exitCode == 131:
        return 'SIGQUIT: ctrl-\, core dumped'
    elif exitCode == 132:
        return 'SIGILL: Malformed, unknown, or priviledged instruction'
    elif exitCode == 133:
        return 'SIGTRAP: Debugger breakpoint'
    elif exitCode == 134:
        return 'SIGABRT: Process itself called abort'
    elif exitCode == 135:
        return 'SIGEMT: Emulator trap'
    elif exitCode == 136:
        return 'SIGFPE: Bad arithmetic operation (e.g. division by zero)'
    elif exitCode == 137:
        return 'SIGKILL (e.g. kill -9 command)'
    elif exitCode ==139:
        return 'SIGSEGV: Segmentation Fault'
    elif exitCode == 143:
        return 'SIGTERM (probably not canceljob or oom)'
    elif exitCode == 151:
        return 'SIGIO: Possible I/O error'
    elif exitCode == 152:
        return 'SIGXCPU: predetermined CPU time used up'
    elif exitCode == 153:
        return 'SIGXFSZ: File larger than maximum size'
    elif 174 <= exitCode <= 253:
        return 'Fatal error signal ' + str(exitCode-128)
    elif exitCode == 254:
        return 'Command invoked cannot execute'
    elif exitCode == 255:
        return 'command not found, possible path problem'
    elif exitCode == 265:
        return 'SIGKILL (e.g. kill -9 command)'
    elif exitCode == 271:
        return 'SIGTERM (e.g. canceljob or oom)'
    else:
        return 'Unknown Error'


def str2secs(time):
	"""
	Convert a string of the form HH:MM:SS into a duration in seconds
	"""
        H, M, S = time.split(':')
        return 3600.0*float(H) + 60.0*float(M) + float(S)

def main():
    """
    this is the main routine.
    """
    #Parse Command-line options
    usage = "usage: %prog [options] [Accounting Files] \n\
        example: %prog -u class01 -u class02 2013*\n\
	example: %prog -s -p jan2013 201301*\n\
	example: %prog -q sw 20130101"
    parser = OptionParser(usage=usage)
    parser.add_option("-u", "--user", dest="user", action="append",\
		      type="string", help="Print stats for user")
    parser.add_option("-j", "--job", dest="jobID", action="append",\
		      type="int", help="Print stats for a job")
    parser.add_option("-q", "--queue", dest="queue", action="append",\
		      type="string", help="Pring stats for a queue")
    parser.add_option("-n", "--node", dest="node", action="append",\
		      type="string", help="Print stats for a node")
    parser.add_option("-p", "--plots", dest="figfile", action="store", \
		      type="string", help="Plot figures")
    parser.add_option("-s", "--sortedlist", dest="list", \
		      action="store_true", default=False,\
		      help="Print a sorted list of users")
    (options, args) = parser.parse_args()
    if options.user == None and options.jobID == None and \
       options.queue == None and options.node == None and \
       options.figfile == None:
	    options.list = True
            filters = None

    if len(args) < 1:
	    sys.exit(usage + '\n \
		     --help for list of options')
    else:
	    joblist = args


    attributes = {}
    items = list()  #users and queues to collect statistics for
    filters = list() #Filters to apply when calling alljobs()
    if options.user != None:
        items += options.user
        filters += options.user
        for u in options.user:
	    attributes[u] = 'user'
    if options.queue != None:
        items += options.queue
        filters += options.queue
        for q in options.queue:
	    attributes[q] = 'queue'
    if options.node != None:
        filters += options.node
    if options.jobID != None:
        filters += str(options.jobID)
    #get list of all jobs
    if len(filters) == 0:
        filters = None
    jobs = alljobs(joblist, filters)
    if len(attributes) > 0:
        itemStats(items, jobs, attributes)
	    

    #Print job info
    if options.jobID != None:
        jobStats(options.jobID, jobs)
    #Print node stats
    if options.node != None:
	    for n in options.node:
		    nodeStats(n, jobs)
    #Make plots
    if options.figfile != None:
	    makePlots(options.figfile, jobs, scatterPlots=True)

    #Sort all users and print list
    if options.list:
        userEffList = list()
        users = {}
        #Add each job to the users dictionary
        for job in jobs:
	    if job.user not in users:
		    users[job.user] = userClass(job)
	    else:
		    users[job.user].joblist.append(job)
        #Build a list of user statistics

        for usr in users:
	    userEffList.append([users[usr].sortMetric(), \
				users[usr].avgEfficiency(), \
				users[usr].avgMemFraction(), \
				users[usr].ttlWalltime()/3600.0, \
				users[usr].name])

        userEffList.sort(reverse=True)
        #Print User statistics
        for usr in userEffList:
	    print(usr[1], usr[2], usr[3], usr[4])
        #Print detailed stats for "top 10" users in sorted list
        for usr in userEffList[:10]:
	    users[usr[4]].printStats()


def itemStats(items, jobs, attributes):
	"""Prints all stats for items of type attribute[item] in jobs list"""
	itemdic = {}
	found = {}
	#Initialize founds to false
	for i in items:
	    found[i] = False
	for job in jobs:
	    for item in items:
	        #Make sure attribute type is reasonable
	        assert attributes[item] in ['queue', 'user']
	        #If job attribute matches item
	        if item == getattr(job, attributes[item]):
		    #If first time finding item in jobs
		    if not found[item]:
		        #Initialize the appropriate item type
		        if 'user' in attributes[item]:
			    itemdic[item] = userClass(job)
			elif 'queue' in attributes[item]:
			    itemdic[item] = queueClass(job)
			#Set found to true
			found[item] = True
		    else:
		        itemdic[item].addJob(job)
	for it in items:
		if found[it]:
			itemdic[it].printStats()
		else:
			print(attributes[it] + " " + it + " not found in joblist")
	return

def jobStats(jobIDs, jobs):
    """Prints all stats for a particular job"""
    found = {}
    for jobID in jobIDs:
        found[jobID] = False
    for job in jobs:
        for jobID in jobIDs:
            if jobID == job.id:
                job.printStats()
                found[jobID] = True
                break
        if found[jobID]:
            break
    for jobID in jobIDs:
        if not found[jobID]:
            print("Job " + str(jobID) + " not found in joblist.")
    return


def nodeStats(node, jobs):
        """Prints all stats for a particular node"""
	nde = None
	found = False
	for job in jobs:
		if any(node in n for n in job.nodes):
			if nde == None:
				nde = nodeClass(job, node)
				found = True
			else:
				nde.addJob(job)
	if found:
		nde.printStats()
	else:
		print("node " + node + " not found in joblist")
	return


									

    
def alljobs(files, filters=None):
    """
    routine to read the accounting logs returning a dictionary of jobs
    """
    alljobs = list()
    walltimesreq = {}
    for file in files:
        try:
		f = open(file, 'r').readlines()
	except IOError:
		sys.exit('IO Error: File ' + file + ' not found')
        for rown in f:
            #When filters are used, lines not containing the filter
            # words are skipped
            if filters != None:
                if not any(filt in rown for filt in filters):
                    continue
	    row = rown.split()
	    cores = 1
            ppn = 0
            gpus = 0
            mics = 0
	    #Exctract the number of cores from the accounting files
            if any('Resource_List.walltime' in s for s in row):
                id = row[1].split(';')[2].split('.')[0]
                for col in row:
                    if 'Resource_List.walltime=' in col:
                        wtreq = col.split('=')[-1]
                walltimesreq[id] = str2secs(wtreq)
	    if any('resources_used' in s for s in row):
	        id = row[1].split(';')[2].split('.')[0]
		date = row[0]
		time = row[1].split(';')[0]
		account = 'unknown'
		for col in row:
		    if 'user=' in col:
			    user = col.split('=')[-1]
		    elif 'queue=' in col:
			    queue = col.split('=')[-1]
		    elif 'cput=' in col:
		        cput = col.split('=')[-1]
		    elif 'used.mem=' in col:
		        mem = col.split('=')[-1]
		    elif 'used.vmem=' in col:
		        vmem = col.split('=')[-1]
		    elif 'resources_used.walltime=' in col:
		        walltime = col.split('=')[-1]
		    elif 'Resource_List.procs=' in col:
		        cores = col.split('=')[-1]
		    elif 'Exit_status=' in col:
		        exitcode = col.split('=')[-1]
		    elif 'account' in col:
		        account = col.split('=')[-1]
		    elif 'jobname' in col:
		        jobname = col.split('=')[-1]
		    elif 'qtime' in col:
			    qtime = col.split('=')[-1]
		    elif 'etime' in col:
			    etime = col.split('=')[-1]
                    elif 'ctime' in col:
                        ctime = col.split('=')[-1]
		    elif 'start' in col:
			    start = col.split('=')[-1]
                    elif 'end' in col:
                        end = col.split('=')[-1]
		    elif 'exec_host' in col:
		        nodes = col.split('=')[-1].split('+')
			nodes = list(set(\
				[node.split('/')[0] for node in nodes]\
				))
		    elif 'Resource_List.nodes=' in col and '-' not in col:
		        col2 = col.split(':')
			if len(col2) > 1:
#			    cores = int(col2[0].split('=')[-1])* \
#				    int(col2[1].split('=')[-1])
#                            ppn = int(col2[1].split('=')[-1])
                            #Todo: Allow the case where both mics and GPUs are used in same job
                            if len(col2) > 2:
                                if 'gpus' in col2[2]:
                                    gpus = int(col2[2].split('=')[-1])
                                elif 'mics' in col2[2]:
                                    mics = int(col2[2].split('=')[-1])
			else:
			    cores = col2[0].split('=')[-1]
                            ppn = 0
                            mics = 0
                            gpus = 0
		try:
		    tiq = int(start) - int(qtime)
		    tie = int(start) - int(etime)
		except(ValueError):
		    tiq = 0
		    tie = 0

                if id in walltimesreq:
                    wtreq = walltimesreq[id]
                else:
                    wtreq = -1
# Added to test KC's method
                if rown.find('exec_host=') > -1:
                    list_hostname=[]
                    for col in row:
                        if 'exec_host=' in col:
                            for hostname_exec in col.split("=")[1].split('+'):
                                list_hostname.append(hostname_exec.split('/')[0])
                    nb_cores_value=len(list_hostname)
 #               if int(nb_cores_value) != int(cores):
                cores = nb_cores_value
                    #print("nodeserror: " + str(id) + " " + str(nb_cores_value) + " " + str(cores))
# End KC's method
                alljobs.append(jobClass(id, user, date, time, queue, \
				   cput, mem, nodes, account, \
				   jobname, vmem, tiq, tie,\
				   walltime, cores, ppn, gpus, \
                                   mics, exitcode, wtreq, \
                                   ctime, etime, qtime, start, end))
    return alljobs

def makePlots(filename, jobs, scatterPlots=False):
        """Creates plots of the job data"""
	efficiencies = list()
	memUnused = list()
	cores = list()
	walltime = list()
	coreHours = list()
	efficienciesCH = list()
	if scatterPlots:
		memUnused2d = list()
		cores2d = list()
		walltime2d = list()
		coreHours2d = list()
	for job in jobs:
		memUnused.append(job.memUnusedFraction()*100.0)
		cores.append(job.cores)
		coreHours.append(job.walltime/3600.0*job.cores)
		walltime.append(job.walltime/3600.0)
		if 0.0 < job.efficiency() < 2.0:
			efficiencies.append(job.efficiency()*100.0)
			if scatterPlots:
				memUnused2d.append(memUnused[-1])
				if job.walltime/3600.0 < 400.0:
				    coreHours2d.append(coreHours[-1])
				    efficienciesCH.append(efficiencies[-1])

	if scatterPlots:
	    plt.clf()
            plt.hexbin(efficiencies, memUnused2d, bins='log', gridsize=1000)
	    plt.xlabel('Efficiency (%)')
	    plt.xlim(0.0, 110.0)
	    plt.ylabel('Unused Memory (%)')
	    plt.ylim(0.0, 100.0)
	    plt.savefig(filename + '.memVsE.png')
	    plt.clf()
	    plt.hexbin(efficienciesCH, coreHours2d, bins='log', \
		       gridsize=(200, 2000))
	    plt.xlabel('Efficiency (%)')
	    plt.xlim(0.0, 110.0)
	    plt.ylabel('Walltime x Cores (core hours)')
	    plt.ylim(0.0, 400.0)
	    plt.savefig(filename + '.coreHoursVsE.png')
	
	plt.clf()
	plt.cla()
	plt.hist(efficiencies, bins=1000, log=True, color='k')
	plt.xlabel('Efficiencies (%)')
	plt.xlim(0.0, 150.0)
	plt.savefig(filename + '.efficiencies.png')
	plt.cla()
	plt.hist(memUnused, bins=1000, log=True, color='k')
	plt.xlabel('Unused Memory (%)')
	plt.xlim(0.0, 110.0)
	plt.savefig(filename + '.memUnused.png')
	plt.cla()
	plt.hist(cores, bins=max(cores), log=True, color='k')
	plt.xlabel('Number of cores')
	plt.xlim(0, 100)
	plt.savefig(filename + '.cores.png')
	plt.cla()
	plt.hist(walltime, bins=1000, log=True, color='k')
	plt.xlim(0, 240.0)
	plt.xlabel('Walltime (hours)')
	plt.savefig(filename + '.walltime.png')
	plt.cla()
	plt.hist(coreHours, bins=1000, log=True, color='k')
	plt.xlim(0, 1000.0)
	plt.xlabel('Walltime x Cores (core hours)')
	plt.savefig(filename + '.corehours.png')
	return


class jobGroup():
	"""
	A class to hold groups of jobs
	"""
	def __init__(self, job):
		self.joblist = list()
		self.joblist.append(job)

	def avgEfficiency(self):
		"""Average efficiency of user's jobs"""
		numJobs = len(self.joblist)
		sumEfficiencies = 0.0
		for job in self.joblist:
			sumEfficiencies += job.efficiency()
		return sumEfficiencies / float(numJobs)
	def avgMem(self):
		"""Average memory of user's jobs"""
		numJobs = len(self.joblist)
		sumMem = 0.0
		for job in self.joblist:
			sumMem += job.mem/job.cores
		return sumMem / float(numJobs)
	def avgMemFraction(self):
		"""Average memory use fraction"""
		sumMem = 0.0
		for job in self.joblist:
			sumMem += 1.0 - job.memUnusedFraction()
		return sumMem / float(len(self.joblist))
	def ttlWalltime(self):
		"""Total walltime*cores"""
		ttlwt = 0.0
		for job in self.joblist:
			ttlwt += job.walltime*float(job.cores)
		return ttlwt
        def gpuHours(self):
            """Total GPU hours (gpus + mics)"""
            gpuh = 0.0
            for job in self.joblist:
                gpuh += job.walltime*(float(job.gpus) + float(job.mics))
            return gpuh
        def avgQtime(self):
            """Average time in queue"""
            avgqt = 0.0
            for job in self.joblist:
                avgqt += job.tiq
            avgqt /= len(self.joblist)
            return avgqt
        def minQtime(self):
            """Shortest time in queue"""
            return min([job.tiq for job in self.joblist])
        def maxQtime(self):
            """Longest time in queue"""
            return max([job.tiq for job in self.joblist])
	
	def addJob(self, job):
            """Append a job to the joblist"""
            self.joblist.append(job)

	def printJobs(self, nJobs):
		"""Print the last nJobs jobs added to user's joblist"""
		for job in self.joblist[-1*nJobs:]:
			print(job.id)

	def printAllJobs(self):
            """Print stats for all jobs in group"""
            for job in self.joblist:
		job.printStats()

	def badExitJobs(self):
            """Create a list of jobs with non-zero exit codes"""
            badExits = list()
            for job in self.joblist:
		if job.exitcode != 0:
			badExits.append(job)
            return badExits
	def fractionBad(self):
		return float(len(self.badExitJobs()))\
		       /float(len(self.joblist))
	def superEfficientJobs(self):
		effJobs = list()
		for job in self.joblist:
			if job.isSuperEfficient():
				effJobs.append(job)
		return effJobs
	def fractionSuperEff(self):
		return float(len(self.superEfficientJobs()))\
		       /float(len(self.joblist))

	def printStats(self):
		"""Print detailed human readable statistics for user"""
		#avgCores is the average number of cores used
		avgCores = 0.0
		for job in self.joblist:
			avgCores += job.cores
		avgCores /= len(self.joblist)
		print('Number of jobs: ' + str(len(self.joblist)))
		print('Average core hours: ' + \
		      str(self.ttlWalltime()/len(self.joblist)/3600.0) \
		      + ' core hours')
		print('Total core hours: ' + \
		      str(self.ttlWalltime()/3600.0) + ' core hours')
                print('Total GPU hours (gpus + mics): ' + \
                      str(self.gpuHours()/3600.0) + ' gpu hours')
                print('Average Queuetime: ' + \
                      str(self.avgQtime()/3600.0) + ' hours')
		print('Average efficiency: ' + \
		      str(self.avgEfficiency()*100.0)\
		      + '%')
		print('Average Number of Cores: ' + \
		      str(avgCores))
		print('Average Memory per core: ' + \
		      str(self.avgMem()/1048576.0) \
		      + ' GB')
	def printBad(self):
		print('Jobs with Bad Exits (' + \
		      str(len(self.badExitJobs())) + \
		      ') (' + str(self.fractionBad()*100.) + \
		      '%):')
		for job in self.badExitJobs()[:10]:
			print(str(job.id) + ' exit code: ' \
			      + str(job.exitcode) + ': ' + ec2str(job.exitcode))
	def printSuperEff(self):
		print('Super-efficient jobs (' + \
		      str(len(self.superEfficientJobs())) + \
		      ') (' + str(self.fractionSuperEff()*100.) + \
		      '%):')
		for job in self.superEfficientJobs()[:10]:
			print(str(job.id) + ' efficiency: ' \
			      + str(job.efficiency()))
        def printTopProp(self, prop, n=5):
            """Prints the most frequent n results of a particular job list member.
            For example, the most frequent users or the most frequent error codes"""
            propdic = {}
            for job in self.joblist:
                if prop == 'node':
                    attr = getattr(job, 'nodes')
                    for node in attr:
                        if node not in propdic:
                            propdic[node] = 1
                        else:
                            propdic[node] += 1
                else:
                    attr = getattr(job, prop)
                    if attr not in propdic:
                        propdic[attr] = 1
                    else:
                        propdic[attr] += 1
            sortedProps = sorted(propdic.items(), reverse=True, key=lambda item: item[1])
            for sp in sortedProps[:n]:
                if prop == 'exitcode':
                    print(str(sp[0]) + ' (' + str(sp[1]) + '): ' + ec2str(sp[0]))
                else:
                    print(str(sp[0]) + ' (' + str(sp[1]) + ', ' + \
                          str(100.0*sp[1]/len(self.joblist)) + '%)')
                
            


class queueClass(jobGroup):
	"""
	A class to hold queue information
	"""
	def __init__(self, job):
		self.queue = job.queue
		jobGroup.__init__(self, job)
	def addJob(self, job):
		assert self.queue == job.queue, \
		       "Error: queue mismatch constructing queue"
		assert any(job.id != j.id for j in self.joblist), \
		       "Error: job %d already added to queue" % job.id
		jobGroup.addJob(self, job)
	def printStats(self):
		"""Print detailed human readable statistics for a queue"""
		#avgCores is the average number of cores used
		print('******************************')
		print('Queue: ' + self.queue)
		jobGroup.printStats(self)
		#print('Some jobs: ')
		#self.printJobs(5)
                print('Top users:')
                self.printTopProp('user')
                print('Most frequently requested core counts:')
                jobGroup.printTopProp(self, 'cores')
                print('Most frequent exit codes:')
                self.printTopProp('exitcode')
		# jobGroup.printBad(self)
		jobGroup.printSuperEff(self)
		print('******************************')

class nodeClass(jobGroup):
	"""
	A class to hold node information
	"""
	def __init__(self, job, node):
		self.node = node
		jobGroup.__init__(self, job)
	def addJob(self, job):
		assert any(self.node in n for n in job.nodes), \
		       "Error: node mismatch constructing node"
		assert any(job.id != j.id for j in self.joblist), \
		       "Error: job %d already added to queue" % job.id
		jobGroup.addJob(self, job)
	def printStats(self):
		"""Print detailed human readable statistics for a node"""
		print('******************************')
		print('Node: ' + self.node)
		jobGroup.printStats(self)
                print('Top users:')
                jobGroup.printTopProp(self, 'user')
                print('Most frequently requested core counts:')
                jobGroup.printTopProp(self, 'cores')
                print('Most frequent exit codes:')
                jobGroup.printTopProp(self, 'exitcode')
		#print('Some jobs: ')
		#self.printJobs(5)
		#jobGroup.printBad(self)
		jobGroup.printSuperEff(self)
		print('******************************')


class userClass(jobGroup):
	"""
	A class to hold user information
	"""
	def __init__(self, job):
		self.name = job.user
		jobGroup.__init__(self, job)

	def addJob(self, job):
		assert self.name == job.user, \
		       "Error: user mismatch constructing user"
		assert any(job.id != j.id for j in self.joblist), \
		       "Error: job %d already added to user" % job.id
		jobGroup.addJob(self, job)
	def sortMetric(self):
		"""Metric used for sorting users"""
		metric = 0.0
		for job in self.joblist:
		    if 0.0 < job.efficiency() < 1.0:
			x = job.efficiency()/(1.0-job.efficiency())
		    else:
		        x = 1.0e24
		    if 0.0 < job.memUnusedFraction() < 1.0:
		        y = (1.0-job.memUnusedFraction())/job.memUnusedFraction()
		    else:
		        y = 1.0e24
		    metric += np.exp(-x)*np.exp(-y)*job.cores*job.walltime
		return metric 
	def printStats(self):
		"""Print detailed human readable statistics for user"""
		#nq is a dictionary mapping queues used to how many jobs
		nq = {}
		#avgCores is the average number of cores used
		for job in self.joblist:
			if job.queue in nq:
				nq[job.queue] += 1
			else:
				nq[job.queue] = 1
		print('******************************')
		print('User: ' + self.name)
		jobGroup.printStats(self)
		print('Queues used (number of jobs):')
		for q in nq:
			print(str(q) + ' (' +  str(nq[q]) + ')')
                print('Most frequent exit codes:')
                jobGroup.printTopProp(self, 'exitcode')
                print('Most frequently requested core counts:')
                jobGroup.printTopProp(self, 'cores')
		#print('Some jobs: ')
		#self.printJobs(5)
		#self.printBad()
		self.printSuperEff()
		print('******************************')
		

class jobClass():
    """
    A class to hold PBS job statistics
    """
    def __init__(self, id, user, date, time, queue, cput, mem, \
		 nodes, account, jobname,\
		 vmem, tiq, tie, walltime, cores, \
                 ppn, gpus, mics, exitcode, walltimereq, \
                 ctime, etime, qtime, start, end):
        #we read everything in as strings (dtype='str'), cast them to floats
        try:
            self.id = int(id)
        except(ValueError):
            self.id = np.nan
        self.user = user
        self.queue = queue
	self.date = date
	self.time = time
	self.nodes = nodes
	self.account = account
	self.jobname = jobname
        try:
            self.cput = str2secs(cput)
        except(ValueError):
            self.cput = np.nan
        try:
            self.mem = float(mem[0:-2])
        except(ValueError):
            self.mem = np.nan
        try:
            self.vmem = float(vmem[0:-2])
        except(ValueError):
            self.vmem = np.nan
	try:
	    self.tiq = int(tiq)
	except(ValueError):
	    self.tiq = 0
	try:
	    self.tie = int(tie)
	except(ValueError):
	    self.tie = 0
        try:
            self.walltime = str2secs(walltime)
	    self.walltime = max(0.1, self.walltime)
        except(ValueError):
            self.walltime = np.nan
	try:
	    self.cores = int(cores)
	except(ValueError):
	    self.cores = 1
        try:
            self.ppn = int(ppn)
        except(ValueError):
            self.ppn = 0
        try: 
            self.gpus = int(gpus)
        except(ValueError):
            self.gpus = 0
        try:
            self.mics = int(mics)
        except(ValueError):
            self.mics = 0
	try:
	    self.exitcode = int(exitcode)
	except(ValueError):
	    self.exitcode = -100
        try:
            self.walltimereq = int(walltimereq)
        except(ValueError):
            self.walltimereq = -1
        try:
            self.ctime = int(ctime)
        except(ValueError):
            self.ctime = -1
        try:
            self.etime = int(etime)
        except(ValueError):
            self.etime = -1
        try:
            self.qtime = int(qtime)
        except(ValueError):
            self.qtime = -1
        try:
            self.start = int(start)
        except(ValueError):
            self.start = -1
        try:
            self.end = int(end)
        except(ValueError):
            self.end = -1
	self.queue = queue
    def efficiency(self):
	    """The CPU usage efficiency of the job"""
	    return self.cput / (self.walltime * float(self.cores))
    def memUnused(self):
	    """ Unused memory in GB """
	    memUsed = self.mem / 1048576.0
	    memPerCore = {'hb':1.7, 'lm':5.7, 'scalemp':8.0, \
			  'lmgpu':5.7, 'sw':2.7}
	    if self.queue in memPerCore:
		    memTotal = memPerCore[self.queue]*self.cores
	    else:
		    memTotal = 3.0*self.cores
	    return (memTotal - memUsed)
    def memUnusedFraction(self):
	    memPerCore = {'hb':1.7, 'lm':5.7, 'scalemp':8.0, \
			  'lmgpu':5.7, 'sw':2.7}
	    if self.queue in memPerCore:
		    return self.memUnused()/(memPerCore[self.queue]*self.cores)
	    else:
		    return self.memUnused()/(3.0*self.cores)
    
    def isSuperEfficient(self):
	    """Returns true if the job has a strange efficiency result"""
	    prob = False
	    if self.cput < 0:
		    prob = True
	    elif self.cput > self.walltime*self.cores:
		    prob = True
	    return prob
    def wasRunningAt(self, time):
        return self.start < time < self.end
    def printStats(self):
	    """Print human readable stats for the job"""
	    print('******************************')
	    print('Job name: ' + str(self.jobname))
	    print('JobID: ' + str(self.id))
	    print('User: ' + str(self.user))
	    print('queue: ' + str(self.queue))
	    print('Completed: ' + str(self.date) + ' ' + str(self.time))
	    print('qtime in Queue: ' + str(self.tiq/3600.0) + ' hours')
	    print('etime in Queue: ' + str(self.tie/3600.0) + ' hours')
	    print('cores: ' + str(self.cores))
	    print('walltime: ' + str(self.walltime/3600.0) + ' hours')
            print('walltime requested: ' + str(self.walltimereq/3600.0) + ' hours')
	    print('cpu time: ' + str(self.cput/3600.0) + ' hours')
	    print('efficiency: ' + str(self.efficiency() * 100.0) + ' %') 
	    print('mem: ' + str(self.mem / 1048576.0) + ' GB')
	    print('vmem: ' + str(self.vmem / 1048576.0) + ' GB')
	    print('exitcode: ' + str(self.exitcode) + ': ' + ec2str(self.exitcode))
	    print('nodes: ' + str(self.nodes))
	    print('******************************')
	    return
	
	    

if __name__ == '__main__':
    main()
