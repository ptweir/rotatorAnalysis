import numpy as np
import pylab
from scipy.stats.mstats import sem
pylab.ion()

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

def plotIt(axAll,axInd,flies,skies,baseDirs, max_num_stops, max_time_stopped):
    if 'noFilter/12trials' in baseDirs:
        individualToPlot = 1#2
    else:
        individualToPlot = 4#2

    PLOTCOLORS = {'diffuserPol/12trials':'k','diffuserPol/sham12trials':'b', 'polDiffuser/12trials':'r','noFilter/12trials':'k', 'noFilter/sham12trials':'b','diffuser/12trials':'r'}
    BASEDIR_ORDER = [5,3,4]
    DOWNSAMPLE_RATE = 26
    UNBIASED = True

    numSamplesInAverages = 130*60*12*2/DOWNSAMPLE_RATE -5#still not strictly correct

    #for b_ind in range(3):
    for b,baseDir in enumerate(baseDirs):
        #b = BASEDIR_ORDER[b_ind]
        #baseDir = baseDirs[b]
        numFlies = len(flies[baseDir])
        results = np.ma.masked_all((numFlies,numSamplesInAverages))
        for fNum in range(numFlies):
            fly = flies[baseDir][fNum].copy()
            sky = skies[baseDir][fNum].copy()
            orientationsAll = np.ma.masked_invalid(fly['orientations'],copy=True)
            timesAll = np.ma.masked_invalid(fly['times'],copy=True)
            timesAll.mask = orientationsAll.mask
            orientations = orientationsAll.compressed()
            times = timesAll.compressed()
            if baseDir in ['diffuserPol/12trials','diffuserPol/sham12trials', 'polDiffuser/12trials']:
                p=2
                orientations = p*orientations
                YMININD, YMAXIND = -.2,.4
                NUMYTICKSIND = 4
                YMINALL, YMAXALL = 0, .4
            else:
                YMININD, YMAXIND = .5,1
                NUMYTICKSIND = 6
                YMINALL, YMAXALL = 0, .5

            numStops = get_num_stops(fly, sky['changeTimes'][0], sky['changeTimes'][-1])
            timeStopped = get_time_stopped(fly, sky['changeTimes'][0], sky['changeTimes'][-1])
                
            if numStops <= max_num_stops and timeStopped <= max_time_stopped:
                
                experimentInds = (times >= sky['changeTimes'][0]) & (times <= sky['changeTimes'][-1])
                experimentOrientations = orientations[experimentInds].copy()
                experimentTimes = times[experimentInds].copy()
                
                downsampledOrientations = experimentOrientations[::DOWNSAMPLE_RATE]
                experimentStartTime = experimentTimes[0]
                timesMinusStart = experimentTimes - experimentStartTime
                downsampledTimes = timesMinusStart[::DOWNSAMPLE_RATE]
                
                orientationsRad = downsampledOrientations*np.pi/180.0
                complexOrientations = np.exp(np.complex(0,1)*orientationsRad)

                meanComplexOrientation = np.mean(complexOrientations)/abs(np.mean(complexOrientations))
                meanOrientation = np.arctan2(meanComplexOrientation.imag,meanComplexOrientation.real)
                #complexOrientationsMinusMean = np.exp(np.complex(0,1)*(orientationsRad-meanOrientation))
                #complexOrientationsMinusMean = complexOrientations / meanComplexOrientation
                complexOrientationsMinusMean = complexOrientations
                resultTimes = np.concatenate((-downsampledTimes[::-1],downsampledTimes[1:]))
                try:
                    result = np.correlate(complexOrientationsMinusMean, complexOrientationsMinusMean, mode='full',old_behavior=False)
                except TypeError:
                    print "running old numpy version"
                    result = np.correlate(complexOrientationsMinusMean, complexOrientationsMinusMean.conjugate(), mode='full')
                result = result.real
                #result = abs(result)
                N = (resultTimes.size+1)/2.0
                if UNBIASED:    
                    bias = 1.0/(N - abs(np.arange(-N+1,N)))
                    result = result*bias
                else:
                    result = result/N
                    
                results[fNum,:] = result[:numSamplesInAverages]
                resultTimesMin = resultTimes/60.0
                #lines = axAll.plot(resultTimesMin,result)
                if (baseDir == 'noFilter/12trials' or baseDir == 'diffuserPol/12trials') and fNum == individualToPlot:
                    lines = axInd.plot(resultTimesMin,result,'k')

        avgLines = axAll.plot(resultTimesMin[:numSamplesInAverages],results.mean(0),color=PLOTCOLORS[baseDir],linewidth=1)
        #avgLines = flyTools.plot_mean_sem(axAll,results,resultTimes[:numSamplesInAverages])
        avgLine = avgLines[0]
        avgLine.set_label(baseDir)
        avgLine.set_zorder(BASEDIR_ORDER[b])
        
        #sqrtNumFliesIncluded = np.sqrt(len(results[:,0].compressed()))
        #patchHandle = axAll.fill_between(resultTimesMin[:numSamplesInAverages],results.mean(0)-results.var(0),results.mean(0)+results.var(0))
        patchHandle = axAll.fill_between(resultTimesMin[:numSamplesInAverages],results.mean(0)-sem(results,0),results.mean(0)+sem(results,0))
        patchHandle.set_facecolor([.8, .8, .8])
        patchHandle.set_edgecolor('none')
        
    for ax in [axAll,axInd]:
        for x in np.linspace(-12,12,13):
            ax.axvline(x,color='g')
        
        XMIN,XMAX = -8,8
        ax.set_xlim((XMIN-.5,XMAX+.5))
        ax.spines['left'].set_position(('outward',8))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        try:
            ax.spines['bottom'].set_bounds(XMIN,XMAX)
        except AttributeError:
            print "running old matplotlib version"
        
        ax.xaxis.set_ticks_position('bottom')
    
    axInd.spines['bottom'].set_visible(False)
    axInd.set_xticklabels([],visible=False)
    axInd.set_xticks([])
    axInd.set_ylim((YMININD,YMAXIND))
    axInd.yaxis.set_ticks_position('left')
    axInd.set_yticks(np.linspace(YMININD,YMAXIND,NUMYTICKSIND))
    axInd.set_ylabel('Autocorrelation')
    
    axAll.spines['bottom'].set_position(('outward',8))
    axAll.set_xticks(np.arange(XMIN,XMAX+1,2))
    axAll.set_xlabel('Time (min)')
    axAll.set_ylim((YMINALL,YMAXALL))
    axAll.yaxis.set_ticks_position('left')
    axAll.set_yticks(np.linspace(YMINALL,YMAXALL,3))
    axAll.set_ylabel('Autocorrelation')
    for ax in [axAll,axInd]:
        for tickLine in ax.get_xticklines() + ax.get_yticklines():
            tickLine.set_markeredgewidth(1)
