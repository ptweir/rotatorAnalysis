import numpy as np
import imp
import pylab
pylab.ion()
#circ = imp.load_source('circ','/home/peter/src/circ/circ.py')
def scatter_categories(ax,data,position,jitter_length,bins):
    #bins = int(np.round((data.max()-data.min())/jitter_length))
    #bins = 10
    n, binEdges, patches = pylab.hist(data,bins = bins,normed=False,visible=False)
    sortedIndices = np.argsort(data)
    y = data[sortedIndices]
    x = position*np.ones(y.shape)
    for binInd, numInBin in enumerate(n):
        binLeftEdge = binEdges[binInd]
        binRightEdge = binEdges[binInd + 1]
        firstElementInBinIndex = np.sum(n[:binInd])
        lastElementInBinIndex = np.sum(n[:binInd])+numInBin
        #ax.axhline(binLeftEdge)
        if numInBin > 1:
            x[firstElementInBinIndex:lastElementInBinIndex] = position + jitter_length*np.arange(numInBin) - jitter_length*(numInBin-1)/2.0
    handle = ax.scatter(x,y)
    return x,sortedIndices,handle
    
def cumprobdist(ax,data,xmax=None,plotArgs={}):
    if xmax is None:
        xmax = np.max(data)
    elif xmax < np.max(data):
        warnings.warn('value of xmax lower than maximum of data')
        xmax = np.max(data)
    num_points = len(data)
    X = np.concatenate(([0.0],data,data,[xmax]))
    X.sort()
    X = X[-1::-1]
    Y = np.concatenate(([0.0],np.arange(num_points),np.arange(num_points)+1,[num_points]))/num_points
    Y.sort()
    line = ax.plot(X,Y,**plotArgs)
    return line[0]
    
def get_time_stopped(fly, beginTime, endTime):
    """calculate total time stopped between beginTime and endTime
    """
    if fly.has_key('stopTimes'):
        a = np.ma.masked_all((2,np.size(fly['startTimes'])))
        a[0,:] = np.copy(fly['startTimes'])
        a[1,:] = beginTime*np.ones(np.shape(fly['startTimes']))
        startTimes = np.max(a,0)
        a[0,:] = np.copy(startTimes)
        a[1,:] = endTime*np.ones(np.shape(fly['startTimes']))
        startTimes = np.min(a,0)
        
        a[0,:] = np.copy(fly['stopTimes'])
        a[1,:] = beginTime*np.ones(np.shape(fly['stopTimes']))
        stopTimes = np.max(a,0)
        a[0,:] = np.copy(stopTimes)
        a[1,:] = endTime*np.ones(np.shape(fly['stopTimes']))
        stopTimes = np.min(a,0)
        time_stopped = np.sum(startTimes - stopTimes)
    else:
        time_stopped = 0
        
    return time_stopped
def get_num_stops(fly, beginTime, endTime):
    """calculate total number of stops between beginTime and endTime
    """
    #num_stops = sum([(sT <= endTime) & (sT >= beginTime) for sT in stopTimes])
    num_stops = 0
    if fly.has_key('stopTimes'):
        stopTimes = np.copy(fly['stopTimes'])
        startTimes = np.copy(fly['startTimes'])
        for i, stopTime in enumerate(stopTimes):
            if stopTime >= beginTime and stopTime <= endTime:
                num_stops += 1
            elif stopTime < beginTime and startTimes[i] >= beginTime:
                num_stops += 1 # started stopped
  
    return num_stops
    
def plotIt(ax,flies,skies,baseDirs, test, max_num_stops, max_time_stopped, chunksPerTrial, maxTimeStoppedChunk):
    if test == 'kuiper':
        kuiper = imp.load_source('kuiper','/home/peter/src/kuiper/kuiper.py')
    elif test == 'fisher':
        fisher = imp.load_source('fisher','/home/peter/src/fisher/fisher.py')
    elif test == 'watsonR':
        from rpy2.robjects.packages import importr
        Rcirc = importr('circular')
        from rpy2.robjects.vectors import FloatVector as RFloatVector
    elif test == 'watsonMatlab':
        from mlabwrap import mlab
    elif test == 'cm':
        from mlabwrap import mlab

    NUM_TRIALS = 12
    ROTATOR_STATE = dict({'U': 0, 'R': 1})

    allDirsTestStatistics = list()
    allDirsPValues = list()

    for baseDirInd, baseDir in enumerate(baseDirs):
        numFlies = len(flies[baseDir])
        meanAngleChunks = np.ma.masked_all((numFlies,NUM_TRIALS,chunksPerTrial)) #all initially masked. Unmasked automatically when assigned a value
        testStatistics = np.ma.masked_all(numFlies)
        pValues = np.ma.masked_all(numFlies)
        for flyInd in range(numFlies):
            fly = flies[baseDir][flyInd].copy()
            sky = skies[baseDir][flyInd].copy()
            if baseDir in ['diffuserPol/12trials','diffuserPol/sham12trials', 'polDiffuser/12trials']:
                alpha = np.ma.masked_invalid(np.mod(-2*fly['orientations']*np.pi/180.0 + np.pi/2 + np.pi,2*np.pi),copy=True)
            else:
                alpha = np.ma.masked_invalid(np.mod(-fly['orientations']*np.pi/180.0 + np.pi/2 + np.pi,2*np.pi),copy=True)
            time = np.ma.masked_invalid(fly['times'],copy=True)
            
            complexAlpha = np.exp(np.complex(0,1)*alpha)
                        
            experimentStartTime = sky['changeTimes'][0]
            experimentEndTime = sky['changeTimes'][12]
            
            timeStopped = get_time_stopped(fly,experimentStartTime,experimentEndTime)
            numStops = get_num_stops(fly,experimentStartTime,experimentEndTime)
            
            if timeStopped <= max_time_stopped and numStops <= max_num_stops:
                for trialInd in range(NUM_TRIALS):
                    trialStartTime = sky['changeTimes'][trialInd]
                    trialEndTime = sky['changeTimes'][trialInd+1]
                    chunkDuration = (trialEndTime - trialStartTime)/chunksPerTrial
                    for chunkInd in range(chunksPerTrial):
                        chunkStartTime = trialStartTime + chunkInd*chunkDuration
                        chunkStartInd = np.argmin(abs(time-chunkStartTime))
                        chunkEndTime = chunkStartTime + chunkDuration
                        chunkEndInd = np.argmin(abs(time-chunkEndTime))
                        
                        timeStoppedChunk = get_time_stopped(fly, chunkStartTime, chunkEndTime)
                        if timeStoppedChunk <= maxTimeStoppedChunk:
                            meanAngleChunkComplex = np.mean(complexAlpha[chunkStartInd:chunkEndInd])
                            meanAngleChunks[flyInd,trialInd,chunkInd] = np.arctan2(meanAngleChunkComplex.imag,meanAngleChunkComplex.real)
                slU = slice(None,None,2)
                slR = slice(1,None,2)
                YMIN, YMAX = 0, 1.0
                if test == 'kuiper':
                    testStat, p_val = kuiper.kuiper_two(meanAngleChunks[flyInd,slU,:].compressed(),meanAngleChunks[flyInd,slR,:].compressed())
                    testStatistics[flyInd] = testStat
                    pValues[flyInd] = p_val
                elif test == 'fisher':
                    testStat, p_val = fisher.fisher_test([meanAngleChunks[flyInd,slU,:].compressed(),meanAngleChunks[flyInd,slR,:].compressed()])
                    testStatistics[flyInd] = testStat
                    #a = circ.circmean(meanAngleChunks[flyInd,slU,:].compressed())
                    #b = circ.circmean(meanAngleChunks[flyInd,slR,:].compressed())
                    #testStatistics[flyInd] = abs(np.arctan2(np.sin(a-b), np.cos(a-b)))
                    pValues[flyInd] = p_val
                    #YMIN, YMAX = -5, 55
                    YMIN, YMAX = -5, 70
                    #YMIN, YMAX = 0, np.pi
                elif test == 'watsonR':
                    RmeanAngleU = Rcirc.circular(RFloatVector(meanAngleChunks[flyInd,slU,:].compressed()))
                    RmeanAngleR = Rcirc.circular(RFloatVector(meanAngleChunks[flyInd,slR,:].compressed()))
                    t = Rcirc.watson_two_test(RmeanAngleU,RmeanAngleR,alpha=.05)
                    testStatistics[flyInd] = np.asarray(t.rx(1))[0][0]
                    pValues[flyInd] = np.asarray(t.rx(1))[0][0]#WRONG
                elif test == 'watsonMatlab':
                    p,table = mlab.circ_wwtest(meanAngleChunks[flyInd,slU,:].compressed(),meanAngleChunks[flyInd,slR,:].compressed(),nout=2)
                    testStatistics[flyInd] = p[0][0]#WRONG
                    pValues[flyInd] = p[0][0]
                elif test == 'cm':
                    p, med, t = mlab.circ_cmtest(meanAngleChunks[flyInd,slU,:].compressed(),meanAngleChunks[flyInd,slR,:].compressed(),nout=3)
                    testStatistics[flyInd] = t[0][0]#CHECK
                    YMAX = 25.0
        allDirsTestStatistics.append(testStatistics.compressed())
        allDirsPValues.append(pValues.compressed())
        bins = np.linspace(YMIN,YMAX,15)
        PLOTCOLORS = ['k','b','r','g','y','c']
        #asc0 = ax.scatter(baseDirInd*np.ones(testStatistics.compressed().shape)+(pylab.rand(testStatistics.compressed().shape[0])-.5)/4.0,testStatistics.compressed(),color=PLOTCOLORS[baseDirInd])
        """
        x, sortedIndices, scatterHandle = scatter_categories(ax,testStatistics.compressed(),baseDirInd*2,.2,bins)
        scatterHandle.set_edgecolor(PLOTCOLORS[baseDirInd])
        scatterHandle.set_facecolor('w')
        sortedTestStatistics=testStatistics.compressed()[sortedIndices]
        sortedPValues = pValues.compressed()[sortedIndices]
        if np.sum(sortedPValues<.05) > 0:
            significantScatterHandle = ax.scatter(x[sortedPValues<.05],sortedTestStatistics[sortedPValues<.05])
            significantScatterHandle.set_facecolor([.5,.5,.5])
        if np.sum(sortedPValues<.01) > 0:
            significantScatterHandle = ax.scatter(x[sortedPValues<.01],sortedTestStatistics[sortedPValues<.01])
            significantScatterHandle.set_facecolor([.1,.1,.1])
        """
        plotArgs = dict(color=PLOTCOLORS[baseDirInd])
        cpLine = cumprobdist(ax,1-pValues.compressed(),xmax=1.1,plotArgs=plotArgs)
        ax.axvline(.95,color='k')
    #asc0.set_label(baseDir)
    #ax.set_title(baseDir)
    #ax.set_ylim((YMIN,YMAX))
    #ax.set_xlim((-1,5))
    #ax.set_xlim((-SECONDS_BEFORE,SECONDS_AFTER))
    ax.spines['left'].set_position(('outward',10))
    ax.spines['bottom'].set_position(('outward',10))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    #ax.set_yticks(np.linspace(YMIN,YMAX,NUM_YTICKS))
    #ax.set_yticklabels(ax.get_yticks()*180/np.pi)
    #ax.set_xticks(np.linspace(-SECONDS_BEFORE,SECONDS_AFTER,5))
    for tickLine in ax.get_xticklines() + ax.get_yticklines():
        tickLine.set_markeredgewidth(1)
    return allDirsTestStatistics, allDirsPValues
    pylab.draw()
"""
fig=pylab.figure()
ax=fig.add_subplot(111)
baseDirs = ['noFilter/12trials', 'noFilter/sham12trials','diffuser/12trials']
test='kuiper'
max_num_stops=4
max_time_stopped=60
plotIt(ax,flies,skies,baseDirs, test, max_num_stops, max_time_stopped)
"""
