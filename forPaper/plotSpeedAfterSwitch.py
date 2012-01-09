import numpy as np
import pylab
from scipy.stats.mstats import sem
from scipy.stats import ttest_1samp
pylab.ion()

def flat_smooth(x,window_len=11):
    if window_len == 1:
        return x
    else:
        s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
        w=np.ones(window_len,'d')
        y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]

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
    
def plotIt(axesList,flies,skies,baseDirs, max_num_stops, max_time_stopped):
    #TITLES = {'diffuserPol/12trials':'Polarizer under \ndiffuser','diffuserPol/sham12trials':'No switching', 'polDiffuser/12trials':'Diffuser under \npolarizer','noFilter/12trials':'Switching', 'noFilter/sham12trials':'No switching','diffuser/12trials':'Diffuser'}
    TITLES = {'diffuserPol/12trials':'Polarized','diffuserPol/sham12trials':'No switching', 'polDiffuser/12trials':'Unpolarized','noFilter/12trials':'Switching', 'noFilter/sham12trials':'No switching','diffuser/12trials':'Diffuser'}
    SECONDS_BEFORE = 10
    SECONDS_AFTER = 10
    SAMPLING_RATE = 125
    NUM_SAMPLES = (SECONDS_AFTER + SECONDS_BEFORE)*SAMPLING_RATE
    #NUM_SAMPLES = 2000
    NUM_SWITCHES = 12
    MIN_EXPERIMENT_TIME = 11
    #MAX_NUM_STOPS = 4
    #MAX_TIME_STOPPED = 60
    SMOOTH_WINDOW_LENGTH = 65
    FONTDICT = {'fontsize':8}
    PLOTCOLORS = ['k','b','r','g','y','c']
    
    TIME_BEFORE_TO_AVERAGE = 10
    TIME_AFTER_TO_AVERAGE = 10
    allSpeedChanges = list()
    #fig = pylab.figure()
    ax1 = axesList[3]
    for baseDirInd, baseDir in enumerate(baseDirs):
        numFlies = len(flies[baseDir])
        velocities = np.ma.masked_all((numFlies,NUM_SAMPLES,NUM_SWITCHES))
        times = np.ma.masked_all((numFlies,NUM_SAMPLES,NUM_SWITCHES))
        speedChange = np.ma.masked_all((numFlies,NUM_SWITCHES))
        for flyInd in range(numFlies):
            fly = flies[baseDir][flyInd].copy()
            sky = skies[baseDir][flyInd].copy()
            if fly['times'][-1] - fly['times'][0] > MIN_EXPERIMENT_TIME*60:
                alpha = np.ma.masked_invalid(np.mod(-fly['orientations']*np.pi/180.0 + np.pi/2 + np.pi,2*np.pi),copy=True)
                time = np.ma.masked_invalid(fly['times'],copy=True)
                
                complexAlpha = np.exp(np.complex(0,1)*alpha)
                smoothedAlpha = flat_smooth(complexAlpha,SMOOTH_WINDOW_LENGTH)
                smoothedAlpha = smoothedAlpha/abs(smoothedAlpha) # should be unnecessary
                #smoothedAngularVel = (smoothedAlpha[1:]/smoothedAlpha[:-1])/np.diff(time)
                ##smoothedAngularVel = (smoothedAlpha[1:]/smoothedAlpha[:-1])/np.mean(np.diff(time))
                a1 = np.arctan2(smoothedAlpha[1:].imag,smoothedAlpha[1:].real)
                a0 = np.arctan2(smoothedAlpha[:-1].imag,smoothedAlpha[:-1].real)
                smoothedAngularVel = np.exp(np.complex(0,1)*(a1-a0))
                smoothedAngularVelToPlot = np.arctan2(smoothedAngularVel.imag,smoothedAngularVel.real)/np.mean(np.diff(time))
                #smoothedAngularVel = flat_smooth(complexAlpha[1:]/complexAlpha[:-1],SMOOTH_WINDOW_LENGTH)/np.mean(np.diff(time))
                #smoothedAngularVel = complexAlpha[1:]/complexAlpha[:-1]/np.mean(np.diff(time))
                ##smoothedAngularVelToPlot = np.arctan2(smoothedAngularVel.imag,smoothedAngularVel.real)
                #smoothedAngularVelToPlot = flat_smooth(np.arctan2(smoothedAngularVel.imag,smoothedAngularVel.real),SMOOTH_WINDOW_LENGTH)

                experimentStartTime = sky['changeTimes'][0]
                experimentEndTime = sky['changeTimes'][12]
                timeStopped = get_time_stopped(fly,experimentStartTime,experimentEndTime)
                numStops = get_num_stops(fly,experimentStartTime,experimentEndTime)
                if timeStopped <= max_time_stopped and numStops <= max_num_stops:
                    for switchNumber in range(NUM_SWITCHES):
                        changeTime = sky['changeTimes'][switchNumber+1]
                        changeInd = np.argmin(abs(time - changeTime))
                        startTime = changeTime - SECONDS_BEFORE
                        startInd = np.argmin(abs(time - startTime))
                        endTime = changeTime + SECONDS_AFTER
                        endInd = np.argmin(abs(time - endTime))
                        indicesToSample = np.arange(startInd,endInd,dtype=int)
                        #indicesToSample = np.array(np.round(np.linspace(startInd,endInd,NUM_SAMPLES)),dtype=int)
                        numStopsDuring = get_num_stops(fly,startTime,endTime)
                        if numStopsDuring == 0 and fly['times'][-1]>endTime:
                            startAvgTime = changeTime-TIME_BEFORE_TO_AVERAGE
                            startAvgInd = np.argmin(abs(time - startAvgTime))
                            endAvgTime = changeTime+TIME_AFTER_TO_AVERAGE
                            endAvgInd = np.argmin(abs(time - endAvgTime))
                            
                            avgSpeedAfter = np.mean(abs(smoothedAngularVelToPlot[changeInd:endAvgInd]))
                            #absAvgAfter = avgAfter + np.complex(0,1)*abs(avgAfter.imag) - np.complex(0,1)*avgAfter.imag
                            avgSpeedBefore = np.mean(abs(smoothedAngularVelToPlot[startAvgInd:changeInd]))
                            #absAvgBefore = avgBefore + np.complex(0,1)*abs(avgBefore.imag) - np.complex(0,1)*avgBefore.imag
                            
                            velocities[flyInd,:,switchNumber] = abs(smoothedAngularVelToPlot[indicesToSample[:NUM_SAMPLES]])
                            times[flyInd,:,switchNumber] = time[indicesToSample[:NUM_SAMPLES]] - time[changeInd]
                            speedChange[flyInd,switchNumber] = avgSpeedAfter - avgSpeedBefore
                    
        PLOT_STEP = 13
        speeds = abs(velocities)
        #speeds = velocities*np.sign(velocities)
        #flySpeeds = np.mean(speeds,2)
        flySpeedsDegPerSec = np.mean(speeds,2)*180/np.pi
        flyTimes = np.mean(times,2)
        ax = axesList[baseDirInd]
        
        meanSpeed = np.mean(flySpeedsDegPerSec,0)[::PLOT_STEP]
        #semToPlot = np.std(flySpeedsDegPerSec,0)[::PLOT_STEP]/np.sqrt(len(flySpeedsDegPerSec[:,0].compressed()))
        semToPlot = sem(flySpeedsDegPerSec,0)[::PLOT_STEP]
        stdToPlot = np.std(flySpeedsDegPerSec,0)[::PLOT_STEP]
        #lineHandle = ax.plot(flyTimes.transpose(),flySpeedsDegPerSec.transpose(),'k')
        lineHandle = ax.plot(np.mean(flyTimes,0)[::PLOT_STEP],meanSpeed)
        lineHandle[0].set_color(PLOTCOLORS[baseDirInd])
        #patchHandle = ax.fill_between(np.mean(flyTimes,0)[::PLOT_STEP],meanSpeed-stdToPlot,meanSpeed+stdToPlot)
        #patchHandle = ax.fill_between(np.mean(flyTimes,0)[::PLOT_STEP],meanSpeed-semToPlot,meanSpeed+semToPlot)
        #patchHandle.set_facecolor([.4, .4, .4])
        #patchHandle.set_edgecolor('none')

        ax.set_title(TITLES[baseDir],FONTDICT)
        if 'noFilter/12trials' in baseDirs:
            YMIN, YMAX = 20, 70
            YSPINEMIN,YSPINEMAX = 30, 50
            ##YMIN, YMAX = .15, .55
            ##YSPINEMIN,YSPINEMAX = .2, .4
        else:
            YMIN, YMAX = 15, 50
            YSPINEMIN,YSPINEMAX =  20, 40
            ##YMIN, YMAX = .1, .35
            ##YSPINEMIN,YSPINEMAX =  .2, .3
        ax.set_ylim((YMIN,YMAX))
        ax.set_xlim((-SECONDS_BEFORE,SECONDS_AFTER))
        ax.spines['left'].set_position(('outward',8))
        ax.spines['bottom'].set_position(('outward',0))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        ax.set_xticks(np.linspace(-SECONDS_BEFORE,SECONDS_AFTER,3))
        ax.set_xlabel('Time (s)')
        if baseDirInd == 0:
            #ax.set_ylabel('Angular speed (deg s' + r'$^{-1} $' + ')')
            ax.set_ylabel('Angular speed (deg s-1)')
            try:
                ax.spines['left'].set_bounds(YSPINEMIN,YSPINEMAX)
                ax.set_yticks(np.linspace(YSPINEMIN,YSPINEMAX,2))
            except AttributeError:
                print "running old matplotlib version"
                #ax.set_yticks(np.linspace(0,YMAX,NUM_YTICKS))
        else:
            ax.set_yticklabels([],visible=False)
            ax.set_yticks([])
            ax.spines['left'].set_visible((False))
        for tickLine in ax.get_xticklines() + ax.get_yticklines():
            tickLine.set_markeredgewidth(1)

        flySpeedChange = np.mean(speedChange,1)
        flySpeedChangeDegPerSec = flySpeedChange*180/np.pi
        boxplotHandle = ax1.boxplot(flySpeedChangeDegPerSec.compressed(),positions=[baseDirInd])
        boxHandle = boxplotHandle['boxes'][0]
        boxHandle.set_color(PLOTCOLORS[baseDirInd])
        for whiskerHandle in boxplotHandle['whiskers']:
            whiskerHandle.set_linestyle('-')
            whiskerHandle.set_color('k')
        for capHandle in boxplotHandle['caps']:
            capHandle.set_visible(False)
        for flierHandle in boxplotHandle['fliers']:
            flierHandle.set_marker('+')
            flierHandle.set_markerfacecolor(PLOTCOLORS[baseDirInd])
            flierHandle.set_markeredgecolor(PLOTCOLORS[baseDirInd]) 
        allSpeedChanges.append(flySpeedChangeDegPerSec.compressed())
    ax1.set_xlim((-.5,len(baseDirs)-.5))
    #YMIN = -.125
    #YMAX = .25
    #ax1.set_ylim((YMIN-.0001,YMAX))
    ax1.spines['left'].set_position(('outward',2))
    for baseDirInd, speedChanges in enumerate(allSpeedChanges):
        t, p_val = ttest_1samp(speedChanges,0)
        if p_val < .001:
            ax1.text(baseDirInd-.25,ax1.get_ylim()[1],'***')
        elif p_val < .01:
            ax1.text(baseDirInd-.25,ax1.get_ylim()[1],'**')        
        elif p_val < .05:
            ax1.text(baseDirInd-.25,ax1.get_ylim()[1],'*')
        elif p_val >=.05:
            ax1.text(baseDirInd-.25,ax1.get_ylim()[1],'NS')
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    try:
        ax1.spines['left'].set_bounds(-10,10)
        ax1.set_yticks(np.linspace(-10,10,3))
    except AttributeError:
        print "running old matplotlib version"
    ax1.yaxis.set_ticks_position('left')
    #ax1.set_yticks(np.linspace(YMIN,YMAX,4))
    #ax1.set_yticklabels(ax1.get_yticks())
    for tickLine in ax1.get_yticklines():
        tickLine.set_markeredgewidth(1)
    #ax1.set_xticks([])
    if 'noFilter/12trials' in baseDirs:
        XLABELS = ['S','N','D']
    else:
        XLABELS = ['P','N','U']
    ax1.xaxis.set_ticks_position('bottom')
    ax1.set_xticks(range(3)) #axAll.set_xticks([])
    ax1.set_xticklabels(XLABELS)
    for ax in axesList[:3]:
        switchPatchHandle = ax.axvspan(0, SECONDS_AFTER)
        switchPatchHandle.set_facecolor([.8,.8,.8])
        switchPatchHandle.set_edgecolor('none')
        switchPatchHandle.set_zorder(-1)
    return allSpeedChanges
        
