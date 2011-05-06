import numpy as np
import pylab
pylab.ion()
import flyTools

DOWNSAMPLE_RATE = 30
OFFSET = 0
UNBIASED = True
MAX_NUM_STOPS=12
MAX_TIME_STOPPED = 120
numSamplesInAverages = 130*60*12*2/DOWNSAMPLE_RATE #still not strictly correct
figAll = pylab.figure()
axAll = figAll.add_subplot(111)
for b, baseDir in enumerate(flies.keys()):
    numFlies = len(flies[baseDir])
    results = np.ma.masked_all((numFlies,numSamplesInAverages))
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    for fNum in range(numFlies):
        fly = flies[baseDir][fNum].copy()
        sky = skies[baseDir][fNum].copy()
        
        print fly['dirName']

        orientations = fly['orientations'].copy()
        times = fly['times'].copy()
        
        numStops = flyTools.get_num_stops(fly, sky['changeTimes'][0], sky['changeTimes'][-1])
        timeStopped = flyTools.get_time_stopped(fly, sky['changeTimes'][0], sky['changeTimes'][-1])
            
        if numStops <= MAX_NUM_STOPS and timeStopped <= MAX_TIME_STOPPED:
            
            experimentInds = (times >= sky['changeTimes'][0]) & (times <= sky['changeTimes'][-1])
            orientations = orientations[experimentInds].copy()
            times = times[experimentInds].copy()
            
            orientations = orientations[::DOWNSAMPLE_RATE]
            orientations = orientations*np.pi/180.0
            complexOrientations = np.exp(np.complex(0,1)*orientations)
            if np.sum(np.isnan(complexOrientations)) != 0:
                print 'tracking failed ', np.sum(np.isnan(complexOrientations)), ' times'
                complexOrientations[np.isnan(complexOrientations)] = 0 #times when tracking failed CHECK?
            #complexOrientations = complexOrientations - np.mean(complexOrientations)
            
            
            experimentStartTime = times[0]
            times = times - experimentStartTime
            times = times[::DOWNSAMPLE_RATE]
            
            if OFFSET > 0:
                timestep = np.median(np.diff(times))
                startInd = int(round(OFFSET/timestep))
                resultTimes = np.concatenate((-times[-startInd-1::-1],times[1:-startInd]))
                result = np.correlate(complexOrientations[startInd:], complexOrientations[:-startInd].conjugate(), mode='full')
            else:
                resultTimes = np.concatenate((-times[::-1],times[1:]))
                result = np.correlate(complexOrientations, complexOrientations.conjugate(), mode='full')
            
            result = result.real
            N = (resultTimes.size+1)/2.0
            if UNBIASED:    
                bias = 1.0/(N - abs(arange(-N+1,N)))
                result = result*bias
            else:
                result = result/N
                
            results[fNum,:] = result[:numSamplesInAverages]
            
            lines = ax.plot(resultTimes,result)
            line = lines[0]
            line.set_label(fly['dirName'][-5:])
    #ax.set_ylim(( 0, int(round(90000.0/DOWNSAMPLE_RATE)) ))
    avgLines = ax.plot(resultTimes[:numSamplesInAverages],results.mean(0),color='r',linewidth=3)
    avgLine = avgLines[0]
    avgLine.set_label('mean')
    ax.set_title(baseDir)
    for x in range(-720,721,120):
        ax.axvline(x,color='k')
    ax.set_xticks(range(-720,720,120))
    ax.legend()
    ax.set_xlabel('time (sec)')
    
    avgLines = axAll.plot(resultTimes[:numSamplesInAverages],results.mean(0))
    avgLine = avgLines[0]
    avgLine.set_label(baseDir)
axAll.set_title('averages')
for x in range(-720,721,120):
    axAll.axvline(x,color='k')
axAll.set_xticks(range(-720,720,120))
axAll.legend()
axAll.set_xlabel('time (sec)')
